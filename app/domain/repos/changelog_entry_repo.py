from abc import ABC, abstractmethod

from app.domain.entities.changelog_entry_entity import ChangelogEntryEntity
from app.domain.inputs.changelog_entry_input import CreateChangelogEntryInput


class ChangelogEntryRepo(ABC):
    @abstractmethod
    def get_by_provider(self, provider_id: int, breaking_only: bool = False) -> list[ChangelogEntryEntity]: ...

    @abstractmethod
    def get_urls_by_provider(self, provider_id: int) -> set[str]: ...

    @abstractmethod
    def create(self, data: CreateChangelogEntryInput) -> ChangelogEntryEntity: ...
