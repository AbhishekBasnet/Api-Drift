from app.usecases.provider_usecase import ProviderUsecase
from scripts.seed_providers import SEED_PROVIDERS, seed_providers
from tests.fakes import FakeProviderRepo


def test_seed_creates_every_provider() -> None:
    repo = FakeProviderRepo()

    created, skipped = seed_providers(ProviderUsecase(repo))

    assert (created, skipped) == (len(SEED_PROVIDERS), 0)
    assert len(repo.providers) == len(SEED_PROVIDERS)


def test_seed_twice_creates_nothing_new() -> None:
    usecase = ProviderUsecase(FakeProviderRepo())
    seed_providers(usecase)

    created, skipped = seed_providers(usecase)

    assert (created, skipped) == (0, len(SEED_PROVIDERS))


def test_seed_slugs_are_unique() -> None:
    slugs = [p.slug for p in SEED_PROVIDERS]

    assert len(slugs) == len(set(slugs))
