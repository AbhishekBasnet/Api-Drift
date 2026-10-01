from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_changelog_controller
from app.api.schemas.changelog_schema import ChangelogEntryResponse
from app.controller.changelog_controller import ChangelogController

router = APIRouter(prefix="/changelog", tags=["changelog"])

ControllerDep = Annotated[ChangelogController, Depends(get_changelog_controller)]


@router.get("/{provider_id}")
def list_entries(provider_id: int, controller: ControllerDep) -> list[ChangelogEntryResponse]:
    return controller.list_entries(provider_id)


@router.post("/{provider_id}/refresh")
def refresh(provider_id: int, controller: ControllerDep) -> list[ChangelogEntryResponse]:
    return controller.refresh(provider_id)
