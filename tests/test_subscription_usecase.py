import pytest

from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.domain.inputs.subscription_input import CreateSubscriptionInput
from app.usecases.subscription_usecase import SubscriptionUsecase
from tests.fakes import FakeProviderRepo, FakeSubscriptionRepo, make_provider


def make_usecase() -> SubscriptionUsecase:
    return SubscriptionUsecase(FakeSubscriptionRepo(), FakeProviderRepo([make_provider()]))


def test_subscribe() -> None:
    usecase = make_usecase()

    subscription = usecase.subscribe(CreateSubscriptionInput(email="a@b.com", provider_id=1))

    assert usecase.list_subscriptions("a@b.com") == [subscription]


def test_subscribe_to_unknown_provider_raises() -> None:
    with pytest.raises(NotFoundError):
        make_usecase().subscribe(CreateSubscriptionInput(email="a@b.com", provider_id=99))


def test_subscribe_twice_raises() -> None:
    usecase = make_usecase()
    usecase.subscribe(CreateSubscriptionInput(email="a@b.com", provider_id=1))

    with pytest.raises(AlreadyExistsError):
        usecase.subscribe(CreateSubscriptionInput(email="a@b.com", provider_id=1))


def test_unsubscribe() -> None:
    usecase = make_usecase()
    subscription = usecase.subscribe(CreateSubscriptionInput(email="a@b.com", provider_id=1))

    usecase.unsubscribe(subscription.id)

    assert usecase.list_subscriptions("a@b.com") == []


def test_unsubscribe_missing_raises() -> None:
    with pytest.raises(NotFoundError):
        make_usecase().unsubscribe(99)
