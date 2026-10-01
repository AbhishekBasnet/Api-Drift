from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_subscription_controller
from app.api.schemas.subscription_schema import SubscriptionCreateRequest, SubscriptionResponse
from app.controller.subscription_controller import SubscriptionController

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

ControllerDep = Annotated[SubscriptionController, Depends(get_subscription_controller)]


@router.get("/")
def list_subscriptions(email: str, controller: ControllerDep) -> list[SubscriptionResponse]:
    return controller.list_subscriptions(email)


@router.post("/", status_code=status.HTTP_201_CREATED)
def subscribe(body: SubscriptionCreateRequest, controller: ControllerDep) -> SubscriptionResponse:
    return controller.subscribe(body)


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def unsubscribe(subscription_id: int, controller: ControllerDep) -> None:
    controller.unsubscribe(subscription_id)
