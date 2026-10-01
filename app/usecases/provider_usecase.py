from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.domain.entities.provider_entity import ProviderEntity
from app.domain.inputs.provider_input import CreateProviderInput
from app.domain.repos.provider_repo import ProviderRepo


class ProviderUsecase:
    def __init__(self, repo: ProviderRepo) -> None:
        self.repo = repo

    def list_providers(self) -> list[ProviderEntity]:
        return self.repo.get_all()

    def get_provider(self, provider_id: int) -> ProviderEntity:
        provider = self.repo.get_by_id(provider_id)
        if provider is None:
            raise NotFoundError("Provider not found")
        return provider

    def create_provider(self, data: CreateProviderInput) -> ProviderEntity:
        if self.repo.get_by_slug(data.slug) is not None:
            raise AlreadyExistsError("A provider with this slug already exists")
        return self.repo.create(data)
