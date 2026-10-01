from app.api.schemas.provider_schema import ProviderCreateRequest, ProviderResponse
from app.domain.entities.provider_entity import ProviderEntity
from app.domain.inputs.provider_input import CreateProviderInput
from app.usecases.provider_usecase import ProviderUsecase


class ProviderController:
    def __init__(self, usecase: ProviderUsecase) -> None:
        self.usecase = usecase

    def list_providers(self) -> list[ProviderResponse]:
        providers = self.usecase.list_providers()
        return [self._to_response(p) for p in providers]

    def get_provider(self, provider_id: int) -> ProviderResponse:
        return self._to_response(self.usecase.get_provider(provider_id))

    def create_provider(self, body: ProviderCreateRequest) -> ProviderResponse:
        data = CreateProviderInput(**body.model_dump())
        return self._to_response(self.usecase.create_provider(data))

    @staticmethod
    def _to_response(provider: ProviderEntity) -> ProviderResponse:
        return ProviderResponse(**provider.model_dump())
