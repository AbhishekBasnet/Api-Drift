from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.controller.changelog_controller import ChangelogController
from app.controller.provider_controller import ProviderController
from app.controller.subscription_controller import SubscriptionController
from app.core.database import get_db
from app.domain.fetchers.changelog_fetcher import ChangelogFetcher
from app.domain.repos.changelog_entry_repo import ChangelogEntryRepo
from app.domain.repos.provider_repo import ProviderRepo
from app.domain.repos.subscription_repo import SubscriptionRepo
from app.infra.clients.feed_changelog_fetcher import FeedChangelogFetcher
from app.infra.repos.db_changelog_entry_repo import DbChangelogEntryRepo
from app.infra.repos.db_provider_repo import DbProviderRepo
from app.infra.repos.db_subscription_repo import DbSubscriptionRepo
from app.usecases.changelog_usecase import ChangelogUsecase
from app.usecases.provider_usecase import ProviderUsecase
from app.usecases.subscription_usecase import SubscriptionUsecase


def get_provider_repo(db: Annotated[Session, Depends(get_db)]) -> ProviderRepo:
    return DbProviderRepo(db)


def get_provider_controller(repo: Annotated[ProviderRepo, Depends(get_provider_repo)]) -> ProviderController:
    return ProviderController(ProviderUsecase(repo))


def get_subscription_repo(db: Annotated[Session, Depends(get_db)]) -> SubscriptionRepo:
    return DbSubscriptionRepo(db)


def get_subscription_controller(
    repo: Annotated[SubscriptionRepo, Depends(get_subscription_repo)],
    provider_repo: Annotated[ProviderRepo, Depends(get_provider_repo)],
) -> SubscriptionController:
    return SubscriptionController(SubscriptionUsecase(repo, provider_repo))


def get_changelog_entry_repo(db: Annotated[Session, Depends(get_db)]) -> ChangelogEntryRepo:
    return DbChangelogEntryRepo(db)


def get_changelog_fetcher() -> ChangelogFetcher:
    return FeedChangelogFetcher()


def get_changelog_controller(
    repo: Annotated[ChangelogEntryRepo, Depends(get_changelog_entry_repo)],
    provider_repo: Annotated[ProviderRepo, Depends(get_provider_repo)],
    fetcher: Annotated[ChangelogFetcher, Depends(get_changelog_fetcher)],
) -> ChangelogController:
    return ChangelogController(ChangelogUsecase(repo, provider_repo, fetcher))
