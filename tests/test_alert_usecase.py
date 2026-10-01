from app.domain.entities.changelog_entry_entity import ChangelogEntryEntity
from app.domain.inputs.subscription_input import CreateSubscriptionInput
from app.usecases.alert_usecase import AlertUsecase
from tests.fakes import NOW, FakeNotifier, FakeSubscriptionRepo, make_provider


def make_entry() -> ChangelogEntryEntity:
    return ChangelogEntryEntity(
        id=1,
        provider_id=1,
        title="v2.0",
        url="https://example.com/v2",
        summary="",
        published_at=NOW,
        is_breaking=True,
        created_at=NOW,
    )


def make_subscriptions(*emails: str) -> FakeSubscriptionRepo:
    repo = FakeSubscriptionRepo()
    for email in emails:
        repo.create(CreateSubscriptionInput(email=email, provider_id=1))
    return repo


def test_notifies_every_subscriber() -> None:
    notifier = FakeNotifier()
    usecase = AlertUsecase(make_subscriptions("a@b.com", "c@d.com"), notifier)

    sent = usecase.notify_breaking_entries(make_provider(), [make_entry()])

    assert sent == 2
    assert [email for email, _ in notifier.sent] == ["a@b.com", "c@d.com"]


def test_one_failed_send_does_not_stop_the_others() -> None:
    notifier = FakeNotifier(failing_emails={"a@b.com"})
    usecase = AlertUsecase(make_subscriptions("a@b.com", "c@d.com"), notifier)

    sent = usecase.notify_breaking_entries(make_provider(), [make_entry()])

    assert sent == 1
    assert [email for email, _ in notifier.sent] == ["c@d.com"]


def test_no_subscribers_sends_nothing() -> None:
    notifier = FakeNotifier()

    sent = AlertUsecase(FakeSubscriptionRepo(), notifier).notify_breaking_entries(make_provider(), [make_entry()])

    assert sent == 0
    assert notifier.sent == []
