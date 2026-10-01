from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_provider_controller
from app.api.schemas.provider_schema import ProviderCreateRequest, ProviderResponse
from app.controller.provider_controller import ProviderController

router = APIRouter(prefix="/providers", tags=["providers"])

ControllerDep = Annotated[ProviderController, Depends(get_provider_controller)]


@router.get("/")
def list_providers(controller: ControllerDep) -> list[ProviderResponse]:
    return controller.list_providers()


@router.get("/{provider_id}")
def get_provider(provider_id: int, controller: ControllerDep) -> ProviderResponse:
    return controller.get_provider(provider_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_provider(body: ProviderCreateRequest, controller: ControllerDep) -> ProviderResponse:
    return controller.create_provider(body)
