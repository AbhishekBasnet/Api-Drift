from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.domain.inputs.provider_input import CreateProviderInput
from app.domain.inputs.subscription_input import CreateSubscriptionInput
from app.infra.repos.db_provider_repo import DbProviderRepo
from app.infra.repos.db_subscription_repo import DbSubscriptionRepo


@pytest.fixture
def db() -> Iterator[Session]:
    engine = create_engine("sqlite://", poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def make_provider(db: Session, slug: str) -> int:
    provider = DbProviderRepo(db).create(
        CreateProviderInput(name=slug, slug=slug, changelog_url=f"https://example.com/{slug}.atom")
    )
    return provider.id


def test_get_by_provider_returns_only_that_providers_subscriptions(db: Session) -> None:
    repo = DbSubscriptionRepo(db)
    stripe, github = make_provider(db, "stripe"), make_provider(db, "github")
    repo.create(CreateSubscriptionInput(email="a@b.com", provider_id=stripe))
    repo.create(CreateSubscriptionInput(email="c@d.com", provider_id=stripe))
    repo.create(CreateSubscriptionInput(email="a@b.com", provider_id=github))

    assert {s.email for s in repo.get_by_provider(stripe)} == {"a@b.com", "c@d.com"}
    assert [s.email for s in repo.get_by_provider(github)] == ["a@b.com"]


def test_get_by_email_and_provider_and_delete(db: Session) -> None:
    repo = DbSubscriptionRepo(db)
    provider_id = make_provider(db, "stripe")
    created = repo.create(CreateSubscriptionInput(email="a@b.com", provider_id=provider_id))

    assert repo.get_by_email_and_provider("a@b.com", provider_id) == created
    assert repo.get_by_email_and_provider("x@y.com", provider_id) is None

    repo.delete(created.id)
    repo.delete(created.id)  # deleting a missing row is a no-op

    assert repo.get_by_id(created.id) is None
