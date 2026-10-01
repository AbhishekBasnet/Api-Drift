from abc import ABC, abstractmethod

from app.domain.entities.provider_entity import ProviderEntity
from app.domain.inputs.provider_input import CreateProviderInput


class ProviderRepo(ABC):
    @abstractmethod
    def get_all(self) -> list[ProviderEntity]: ...

    @abstractmethod
    def get_by_id(self, provider_id: int) -> ProviderEntity | None: ...

    @abstractmethod
    def get_by_slug(self, slug: str) -> ProviderEntity | None: ...

    @abstractmethod
    def create(self, data: CreateProviderInput) -> ProviderEntity: ...
