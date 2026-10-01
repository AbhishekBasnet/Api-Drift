from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.domain.entities.subscription_entity import SubscriptionEntity
from app.domain.inputs.subscription_input import CreateSubscriptionInput
from app.domain.repos.provider_repo import ProviderRepo
from app.domain.repos.subscription_repo import SubscriptionRepo


class SubscriptionUsecase:
    def __init__(self, repo: SubscriptionRepo, provider_repo: ProviderRepo) -> None:
        self.repo = repo
        self.provider_repo = provider_repo

    def list_subscriptions(self, email: str) -> list[SubscriptionEntity]:
        return self.repo.get_by_email(email)

    def subscribe(self, data: CreateSubscriptionInput) -> SubscriptionEntity:
        if self.provider_repo.get_by_id(data.provider_id) is None:
            raise NotFoundError("Provider not found")
        if self.repo.get_by_email_and_provider(data.email, data.provider_id) is not None:
            raise AlreadyExistsError("Already subscribed to this provider")
        return self.repo.create(data)

    def unsubscribe(self, subscription_id: int) -> None:
        if self.repo.get_by_id(subscription_id) is None:
            raise NotFoundError("Subscription not found")
        self.repo.delete(subscription_id)
