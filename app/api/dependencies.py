from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.controller.provider_controller import ProviderController
from app.core.database import get_db
from app.domain.repos.provider_repo import ProviderRepo
from app.infra.repos.db_provider_repo import DbProviderRepo
from app.usecases.provider_usecase import ProviderUsecase


def get_provider_repo(db: Annotated[Session, Depends(get_db)]) -> ProviderRepo:
    return DbProviderRepo(db)


def get_provider_controller(repo: Annotated[ProviderRepo, Depends(get_provider_repo)]) -> ProviderController:
    return ProviderController(ProviderUsecase(repo))
