from app.api.schemas.subscription_schema import SubscriptionCreateRequest, SubscriptionResponse
from app.domain.entities.subscription_entity import SubscriptionEntity
from app.domain.inputs.subscription_input import CreateSubscriptionInput
from app.usecases.subscription_usecase import SubscriptionUsecase


class SubscriptionController:
    def __init__(self, usecase: SubscriptionUsecase) -> None:
        self.usecase = usecase

    def list_subscriptions(self, email: str) -> list[SubscriptionResponse]:
        subscriptions = self.usecase.list_subscriptions(email)
        return [self._to_response(s) for s in subscriptions]

    def subscribe(self, body: SubscriptionCreateRequest) -> SubscriptionResponse:
        data = CreateSubscriptionInput(**body.model_dump())
        return self._to_response(self.usecase.subscribe(data))

    def unsubscribe(self, subscription_id: int) -> None:
        self.usecase.unsubscribe(subscription_id)

    @staticmethod
    def _to_response(subscription: SubscriptionEntity) -> SubscriptionResponse:
        return SubscriptionResponse(**subscription.model_dump())
