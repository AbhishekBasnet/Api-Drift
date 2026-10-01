from typing import override

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.subscription_entity import SubscriptionEntity
from app.domain.inputs.subscription_input import CreateSubscriptionInput
from app.domain.repos.subscription_repo import SubscriptionRepo
from app.infra.models.subscription_model import SubscriptionModel


class DbSubscriptionRepo(SubscriptionRepo):
    def __init__(self, db: Session) -> None:
        self.db = db

    @override
    def get_by_email(self, email: str) -> list[SubscriptionEntity]:
        rows = self.db.scalars(select(SubscriptionModel).where(SubscriptionModel.email == email)).all()
        return [SubscriptionEntity.model_validate(row) for row in rows]

    @override
    def get_by_id(self, subscription_id: int) -> SubscriptionEntity | None:
        row = self.db.get(SubscriptionModel, subscription_id)
        return SubscriptionEntity.model_validate(row) if row else None

    @override
    def get_by_email_and_provider(self, email: str, provider_id: int) -> SubscriptionEntity | None:
        row = self.db.scalar(
            select(SubscriptionModel).where(
                SubscriptionModel.email == email, SubscriptionModel.provider_id == provider_id
            )
        )
        return SubscriptionEntity.model_validate(row) if row else None

    @override
    def create(self, data: CreateSubscriptionInput) -> SubscriptionEntity:
        row = SubscriptionModel(**data.model_dump())
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return SubscriptionEntity.model_validate(row)

    @override
    def delete(self, subscription_id: int) -> None:
        row = self.db.get(SubscriptionModel, subscription_id)
        if row:
            self.db.delete(row)
            self.db.commit()
