from typing import override

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.changelog_entry_entity import ChangelogEntryEntity
from app.domain.inputs.changelog_entry_input import CreateChangelogEntryInput
from app.domain.repos.changelog_entry_repo import ChangelogEntryRepo
from app.infra.models.changelog_entry_model import ChangelogEntryModel


class DbChangelogEntryRepo(ChangelogEntryRepo):
    def __init__(self, db: Session) -> None:
        self.db = db

    @override
    def get_by_provider(self, provider_id: int) -> list[ChangelogEntryEntity]:
        rows = self.db.scalars(
            select(ChangelogEntryModel)
            .where(ChangelogEntryModel.provider_id == provider_id)
            .order_by(ChangelogEntryModel.published_at.desc())
        ).all()
        return [ChangelogEntryEntity.model_validate(row) for row in rows]

    @override
    def get_urls_by_provider(self, provider_id: int) -> set[str]:
        urls = self.db.scalars(select(ChangelogEntryModel.url).where(ChangelogEntryModel.provider_id == provider_id))
        return set(urls)

    @override
    def create(self, data: CreateChangelogEntryInput) -> ChangelogEntryEntity:
        row = ChangelogEntryModel(**data.model_dump())
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return ChangelogEntryEntity.model_validate(row)
