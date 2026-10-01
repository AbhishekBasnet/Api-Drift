from app.api.schemas.changelog_schema import ChangelogEntryResponse
from app.domain.entities.changelog_entry_entity import ChangelogEntryEntity
from app.usecases.changelog_usecase import ChangelogUsecase


class ChangelogController:
    def __init__(self, usecase: ChangelogUsecase) -> None:
        self.usecase = usecase

    def list_entries(self, provider_id: int) -> list[ChangelogEntryResponse]:
        return [self._to_response(e) for e in self.usecase.list_entries(provider_id)]

    def refresh(self, provider_id: int) -> list[ChangelogEntryResponse]:
        return [self._to_response(e) for e in self.usecase.refresh(provider_id)]

    @staticmethod
    def _to_response(entry: ChangelogEntryEntity) -> ChangelogEntryResponse:
        return ChangelogEntryResponse(**entry.model_dump())
