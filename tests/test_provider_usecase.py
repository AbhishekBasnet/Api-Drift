import pytest

from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.domain.inputs.provider_input import CreateProviderInput
from app.usecases.provider_usecase import ProviderUsecase
from tests.fakes import FakeProviderRepo, make_provider


def make_input(slug: str = "stripe") -> CreateProviderInput:
    return CreateProviderInput(name="Stripe", slug=slug, changelog_url="https://example.com/feed.atom")


def test_create_provider() -> None:
    usecase = ProviderUsecase(FakeProviderRepo())

    provider = usecase.create_provider(make_input())

    assert provider.slug == "stripe"
    assert usecase.list_providers() == [provider]


def test_create_provider_with_duplicate_slug_raises() -> None:
    usecase = ProviderUsecase(FakeProviderRepo([make_provider(slug="stripe")]))

    with pytest.raises(AlreadyExistsError):
        usecase.create_provider(make_input("stripe"))


def test_get_missing_provider_raises() -> None:
    usecase = ProviderUsecase(FakeProviderRepo())

    with pytest.raises(NotFoundError):
        usecase.get_provider(99)
