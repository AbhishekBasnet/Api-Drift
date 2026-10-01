import pytest

from app.core.exceptions import FetchError, NotFoundError
from app.domain.inputs.changelog_entry_input import FetchedEntryInput
from app.domain.inputs.subscription_input import CreateSubscriptionInput
from app.domain.services.breaking_change_classifier import BreakingChangeClassifier
from app.usecases.alert_usecase import AlertUsecase
from app.usecases.changelog_usecase import ChangelogUsecase
from tests.fakes import (
    FakeChangelogEntryRepo,
    FakeFetcher,
    FakeNotifier,
    FakeProviderRepo,
    FakeSubscriptionRepo,
    make_fetched,
    make_provider,
)

PROVIDER = make_provider()
BROKEN = make_provider(provider_id=2, name="Broken", slug="broken")
OLD = make_fetched("v1.0", "https://example.com/v1")
NEW_BREAKING = make_fetched("v2.0", "https://example.com/v2", "Removed the client_id field")
NEW_SAFE = make_fetched("v1.1", "https://example.com/v1.1", "Improved error messages")


class Setup:
    def __init__(self) -> None:
        self.fetcher = FakeFetcher()
        self.notifier = FakeNotifier()
        self.subscriptions = FakeSubscriptionRepo()
        self.subscriptions.create(CreateSubscriptionInput(email="a@b.com", provider_id=PROVIDER.id))
        self.usecase = ChangelogUsecase(
            FakeChangelogEntryRepo(),
            FakeProviderRepo([PROVIDER, BROKEN]),
            self.fetcher,
            BreakingChangeClassifier(),
            AlertUsecase(self.subscriptions, self.notifier),
        )

    def set_feed(self, *entries: FetchedEntryInput) -> None:
        self.fetcher.feeds[PROVIDER.changelog_url] = list(entries)


def test_refresh_stores_and_classifies_entries() -> None:
    setup = Setup()
    setup.set_feed(OLD, NEW_BREAKING)

    stored = setup.usecase.refresh(PROVIDER.id)

    assert {e.title: e.is_breaking for e in stored} == {"v1.0": False, "v2.0": True}


def test_refresh_skips_entries_it_already_has() -> None:
    setup = Setup()
    setup.set_feed(OLD)
    setup.usecase.refresh(PROVIDER.id)

    assert setup.usecase.refresh(PROVIDER.id) == []


def test_first_refresh_sends_no_alerts() -> None:
    setup = Setup()
    setup.set_feed(OLD, NEW_BREAKING)

    setup.usecase.refresh(PROVIDER.id)

    assert setup.notifier.sent == []


def test_later_breaking_entry_sends_alert() -> None:
    setup = Setup()
    setup.set_feed(OLD)
    setup.usecase.refresh(PROVIDER.id)
    setup.set_feed(OLD, NEW_BREAKING)

    setup.usecase.refresh(PROVIDER.id)

    assert [email for email, _ in setup.notifier.sent] == ["a@b.com"]


def test_later_safe_entry_sends_no_alert() -> None:
    setup = Setup()
    setup.set_feed(OLD)
    setup.usecase.refresh(PROVIDER.id)
    setup.set_feed(OLD, NEW_SAFE)

    setup.usecase.refresh(PROVIDER.id)

    assert setup.notifier.sent == []


def test_refresh_all_continues_after_a_failing_provider() -> None:
    setup = Setup()
    setup.fetcher.feeds[BROKEN.changelog_url] = FetchError("down")
    setup.set_feed(OLD)

    assert setup.usecase.refresh_all() == 1


def test_list_entries_can_filter_breaking_only() -> None:
    setup = Setup()
    setup.set_feed(OLD, NEW_BREAKING)
    setup.usecase.refresh(PROVIDER.id)

    entries = setup.usecase.list_entries(PROVIDER.id, breaking_only=True)

    assert [e.title for e in entries] == ["v2.0"]


def test_refresh_unknown_provider_raises() -> None:
    with pytest.raises(NotFoundError):
        Setup().usecase.refresh(99)
