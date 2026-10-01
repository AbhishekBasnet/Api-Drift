# API Drift

A small FastAPI service that watches the changelogs of third-party APIs (Stripe, Twilio, OpenAI, ...) and emails you
when a new release looks like a **breaking change**. Think "Dependabot for API breaking changes".

## What it does

1. You add a **provider**: a name and the URL of its changelog feed (RSS or Atom).
2. Someone **subscribes** an email address to that provider.
3. The app **refreshes** the feed, stores every new entry and **classifies** it as breaking or not.
4. If a new entry looks breaking, every subscriber of that provider gets an **alert**.

Refreshing happens automatically on a timer, or on demand through the API.

## Quick start

You need [uv](https://docs.astral.sh/uv/), Python 3.14 and a PostgreSQL database.

```bash
uv sync                      # install dependencies
cp .env.example .env         # then edit DATABASE_URL
make seed                    # optional: load 7 default providers
uv run fastapi dev           # http://localhost:8000/docs
```

The tables are created on startup, but the database itself must exist. With the Postgres container used in
development:

```bash
docker exec dev.postgres createdb -U Joshua apidrift
```

### Running in Docker

```bash
make up      # build and start with hot reload, http://localhost:3333/docs
make down    # stop and remove the containers
```

The app container joins the `dev-postgres_default` Docker network and reaches the database through
`DOCKER_DATABASE_URL` (host `dev.postgres`, port `5432`). Set it in your `.env`.

### Other commands

| Command     | What it does                                   |
|-------------|------------------------------------------------|
| `make test` | Run the test suite                             |
| `make seed` | Add the default providers (safe to run twice)  |
| `make sync` | Install dependencies with uv                   |

## Architecture

The code follows clean architecture. Every request goes through the same layers, and each layer only knows about the
ones **below** it:

```
Router → Controller → Usecase → Repo interface ← Repo implementation
 (HTTP)   (response)   (rules)     (domain)          (database)
```

| Layer | Folder | Job |
|-------|--------|-----|
| Router | `app/api/` | HTTP only: paths, status codes, request and response schemas |
| Controller | `app/controller/` | Calls one usecase and turns entities into response schemas |
| Usecase | `app/usecases/` | The business rules (duplicates, 404s, first-sync, alerts) |
| Domain | `app/domain/` | Plain Python and Pydantic: entities, inputs, abstract repos, the classifier |
| Infrastructure | `app/infra/` | The real work: SQLAlchemy models and repos, the feed fetcher, the email sender |
| Core | `app/core/` | Settings, database session, exceptions |

The important rule: **usecases depend on interfaces, never on SQLAlchemy or HTTP.** The abstract repos, the fetcher
and the notifier are defined in `domain/`, and `infra/` implements them. That is why the usecases can be tested with
small in-memory fakes and no database.

### Folder map

```
main.py                 App setup, error handlers, background job startup
app/
  api/                  Routers, schemas and dependencies.py (wires the layers with Depends)
  controller/           ProviderController, SubscriptionController, ChangelogController
  usecases/             ProviderUsecase, SubscriptionUsecase, ChangelogUsecase, AlertUsecase
  domain/
    entities/           What comes back from repos (ProviderEntity, ...)
    inputs/             What goes into repos (CreateProviderInput, ...)
    repos/              Abstract repo interfaces
    fetchers/           ChangelogFetcher interface
    notifiers/          AlertNotifier interface
    services/           BreakingChangeClassifier
  infra/
    models/             SQLAlchemy tables
    repos/              Db*Repo classes implementing the interfaces
    clients/            Feed fetcher, SMTP and log notifiers
  jobs/                 Background refresh loop
  container.py          Builds the changelog usecase (used by the routes and the job)
  core/                 Settings, database, exceptions
scripts/                seed_providers.py
tests/                  Fakes and tests
```

### Following one request

`POST /changelog/{provider_id}/refresh`:

1. **Router** (`changelog_router.py`) receives the call and hands it to the controller.
2. **Controller** calls `ChangelogUsecase.refresh()`.
3. **Usecase** loads the provider, asks the **fetcher** for the feed, skips URLs it already stores, classifies each
   new entry, saves it through the **repo** and, if a new entry is breaking, asks `AlertUsecase` to notify the
   subscribers.
4. **Controller** converts the saved entities into response schemas and the router returns them.

### How breaking changes are detected

`BreakingChangeClassifier` uses plain keyword rules, no AI:

- "breaking" or the ⚠ sign always counts (but "no breaking changes" does not).
- Words like *removed*, *deprecated*, *renamed*, *no longer*, *drop support*, *sunset* count too.
- Each **line** of an entry is judged on its own, and a line that talks about docs, examples, descriptions, typos or
  tests is ignored.

It is cheap and easy to explain, but it is a first filter, not a perfect one (see Limitations).
