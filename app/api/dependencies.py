from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.controller.provider_controller import ProviderController
from app.controller.subscription_controller import SubscriptionController
from app.core.database import get_db
from app.domain.repos.provider_repo import ProviderRepo
from app.domain.repos.subscription_repo import SubscriptionRepo
from app.infra.repos.db_provider_repo import DbProviderRepo
from app.infra.repos.db_subscription_repo import DbSubscriptionRepo
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
