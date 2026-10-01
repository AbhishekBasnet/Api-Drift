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
