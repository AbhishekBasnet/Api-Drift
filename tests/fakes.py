from datetime import UTC, datetime
from typing import override

from app.core.exceptions import NotifyError
from app.domain.entities.changelog_entry_entity import ChangelogEntryEntity
from app.domain.entities.provider_entity import ProviderEntity
from app.domain.entities.subscription_entity import SubscriptionEntity
from app.domain.fetchers.changelog_fetcher import ChangelogFetcher
from app.domain.inputs.changelog_entry_input import CreateChangelogEntryInput, FetchedEntryInput
from app.domain.inputs.provider_input import CreateProviderInput
from app.domain.inputs.subscription_input import CreateSubscriptionInput
from app.domain.notifiers.alert_notifier import AlertNotifier
from app.domain.repos.changelog_entry_repo import ChangelogEntryRepo
from app.domain.repos.provider_repo import ProviderRepo
from app.domain.repos.subscription_repo import SubscriptionRepo

NOW = datetime(2026, 10, 1, tzinfo=UTC)


def make_provider(provider_id: int = 1, name: str = "Stripe", slug: str = "stripe") -> ProviderEntity:
    return ProviderEntity(
        id=provider_id, name=name, slug=slug, changelog_url=f"https://example.com/{slug}.atom", created_at=NOW
    )


def make_fetched(title: str, url: str, summary: str = "") -> FetchedEntryInput:
    return FetchedEntryInput(title=title, url=url, summary=summary, published_at=NOW)


class FakeProviderRepo(ProviderRepo):
    def __init__(self, providers: list[ProviderEntity] | None = None) -> None:
        self.providers = providers or []

    @override
    def get_all(self) -> list[ProviderEntity]:
        return self.providers

    @override
    def get_by_id(self, provider_id: int) -> ProviderEntity | None:
        return next((p for p in self.providers if p.id == provider_id), None)

    @override
    def get_by_slug(self, slug: str) -> ProviderEntity | None:
        return next((p for p in self.providers if p.slug == slug), None)

    @override
    def create(self, data: CreateProviderInput) -> ProviderEntity:
        provider = ProviderEntity(id=len(self.providers) + 1, created_at=NOW, **data.model_dump())
        self.providers.append(provider)
        return provider


class FakeSubscriptionRepo(SubscriptionRepo):
    def __init__(self) -> None:
        self.subscriptions: list[SubscriptionEntity] = []

    @override
    def get_by_email(self, email: str) -> list[SubscriptionEntity]:
        return [s for s in self.subscriptions if s.email == email]

    @override
    def get_by_provider(self, provider_id: int) -> list[SubscriptionEntity]:
        return [s for s in self.subscriptions if s.provider_id == provider_id]

    @override
    def get_by_id(self, subscription_id: int) -> SubscriptionEntity | None:
        return next((s for s in self.subscriptions if s.id == subscription_id), None)

    @override
    def get_by_email_and_provider(self, email: str, provider_id: int) -> SubscriptionEntity | None:
        return next((s for s in self.subscriptions if s.email == email and s.provider_id == provider_id), None)

    @override
    def create(self, data: CreateSubscriptionInput) -> SubscriptionEntity:
        subscription = SubscriptionEntity(id=len(self.subscriptions) + 1, created_at=NOW, **data.model_dump())
        self.subscriptions.append(subscription)
        return subscription

    @override
    def delete(self, subscription_id: int) -> None:
        self.subscriptions = [s for s in self.subscriptions if s.id != subscription_id]


class FakeChangelogEntryRepo(ChangelogEntryRepo):
    def __init__(self) -> None:
        self.entries: list[ChangelogEntryEntity] = []

    @override
    def get_by_provider(self, provider_id: int, breaking_only: bool = False) -> list[ChangelogEntryEntity]:
        return [e for e in self.entries if e.provider_id == provider_id and (e.is_breaking or not breaking_only)]

    @override
    def get_urls_by_provider(self, provider_id: int) -> set[str]:
        return {e.url for e in self.entries if e.provider_id == provider_id}

    @override
    def create(self, data: CreateChangelogEntryInput) -> ChangelogEntryEntity:
        entry = ChangelogEntryEntity(id=len(self.entries) + 1, created_at=NOW, **data.model_dump())
        self.entries.append(entry)
        return entry


class FakeFetcher(ChangelogFetcher):
    def __init__(self) -> None:
        self.feeds: dict[str, list[FetchedEntryInput] | Exception] = {}

    @override
    def fetch(self, url: str) -> list[FetchedEntryInput]:
        feed = self.feeds.get(url, [])
        if isinstance(feed, Exception):
            raise feed
        return feed


class FakeNotifier(AlertNotifier):
    def __init__(self, failing_emails: set[str] | None = None) -> None:
        self.sent: list[tuple[str, str]] = []
        self.failing_emails = failing_emails or set()

    @override
    def send(self, to_email: str, subject: str, body: str) -> None:
        if to_email in self.failing_emails:
            raise NotifyError(f"cannot send to {to_email}")
        self.sent.append((to_email, subject))
