from sqlalchemy.orm import Session

from app.core.settings import settings
from app.domain.notifiers.alert_notifier import AlertNotifier
from app.domain.services.breaking_change_classifier import BreakingChangeClassifier
from app.infra.clients.feed_changelog_fetcher import FeedChangelogFetcher
from app.infra.clients.log_alert_notifier import LogAlertNotifier
from app.infra.clients.smtp_alert_notifier import SmtpAlertNotifier
from app.infra.repos.db_changelog_entry_repo import DbChangelogEntryRepo
from app.infra.repos.db_provider_repo import DbProviderRepo
from app.infra.repos.db_subscription_repo import DbSubscriptionRepo
from app.usecases.alert_usecase import AlertUsecase
from app.usecases.changelog_usecase import ChangelogUsecase


def get_alert_notifier() -> AlertNotifier:
    if settings.SMTP_HOST:
        return SmtpAlertNotifier(settings)
    return LogAlertNotifier()


def build_changelog_usecase(db: Session) -> ChangelogUsecase:
    alert_usecase = AlertUsecase(DbSubscriptionRepo(db), get_alert_notifier())
    return ChangelogUsecase(
        DbChangelogEntryRepo(db),
        DbProviderRepo(db),
        FeedChangelogFetcher(),
        BreakingChangeClassifier(),
        alert_usecase,
    )
