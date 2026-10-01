from abc import ABC, abstractmethod

from app.domain.entities.subscription_entity import SubscriptionEntity
from app.domain.inputs.subscription_input import CreateSubscriptionInput


class SubscriptionRepo(ABC):
    @abstractmethod
    def get_by_email(self, email: str) -> list[SubscriptionEntity]: ...

    @abstractmethod
    def get_by_id(self, subscription_id: int) -> SubscriptionEntity | None: ...

    @abstractmethod
    def get_by_email_and_provider(self, email: str, provider_id: int) -> SubscriptionEntity | None: ...

    @abstractmethod
    def create(self, data: CreateSubscriptionInput) -> SubscriptionEntity: ...

    @abstractmethod
    def delete(self, subscription_id: int) -> None: ...
