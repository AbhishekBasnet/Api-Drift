from typing import override

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.provider_entity import ProviderEntity
from app.domain.inputs.provider_input import CreateProviderInput
from app.domain.repos.provider_repo import ProviderRepo
from app.infra.models.provider_model import ProviderModel


class DbProviderRepo(ProviderRepo):
    def __init__(self, db: Session) -> None:
        self.db = db

    @override
    def get_all(self) -> list[ProviderEntity]:
        rows = self.db.scalars(select(ProviderModel).order_by(ProviderModel.name)).all()
        return [ProviderEntity.model_validate(row) for row in rows]

    @override
    def get_by_id(self, provider_id: int) -> ProviderEntity | None:
        row = self.db.get(ProviderModel, provider_id)
        return ProviderEntity.model_validate(row) if row else None

    @override
    def get_by_slug(self, slug: str) -> ProviderEntity | None:
        row = self.db.scalar(select(ProviderModel).where(ProviderModel.slug == slug))
        return ProviderEntity.model_validate(row) if row else None

    @override
    def create(self, data: CreateProviderInput) -> ProviderEntity:
        row = ProviderModel(**data.model_dump())
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return ProviderEntity.model_validate(row)
