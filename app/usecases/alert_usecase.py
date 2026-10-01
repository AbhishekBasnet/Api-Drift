import logging

from app.core.exceptions import NotifyError
from app.domain.entities.changelog_entry_entity import ChangelogEntryEntity
from app.domain.entities.provider_entity import ProviderEntity
from app.domain.notifiers.alert_notifier import AlertNotifier
from app.domain.repos.subscription_repo import SubscriptionRepo

logger = logging.getLogger("uvicorn.error")


class AlertUsecase:
    def __init__(self, subscription_repo: SubscriptionRepo, notifier: AlertNotifier) -> None:
        self.subscription_repo = subscription_repo
        self.notifier = notifier

    def notify_breaking_entries(self, provider: ProviderEntity, entries: list[ChangelogEntryEntity]) -> int:
        subscriptions = self.subscription_repo.get_by_provider(provider.id)
        sent = 0
        for entry in entries:
            subject = f"[API Drift] Possible breaking change in {provider.name}: {entry.title}"
            body = (
                f"{provider.name} published a release that looks like a breaking change.\n\n{entry.title}\n{entry.url}"
            )
            for subscription in subscriptions:
                try:
                    self.notifier.send(subscription.email, subject, body)
                    sent += 1
                except NotifyError:
                    logger.exception("Failed to alert %s about %s", subscription.email, entry.url)
        return sent
