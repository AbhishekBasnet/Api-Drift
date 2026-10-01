import pytest
from fastapi.testclient import TestClient

from app.domain.inputs.changelog_entry_input import FetchedEntryInput
from app.infra.clients.feed_changelog_fetcher import FeedChangelogFetcher
from tests.fakes import make_fetched

PROVIDER_BODY = {"name": "Stripe", "slug": "stripe", "changelog_url": "https://example.com/feed.atom"}


def create_provider(client: TestClient) -> int:
    return client.post("/providers/", json=PROVIDER_BODY).json()["id"]


def test_health(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_create_and_get_provider(client: TestClient) -> None:
    created = client.post("/providers/", json=PROVIDER_BODY)

    assert created.status_code == 201
    assert client.get(f"/providers/{created.json()['id']}").json()["slug"] == "stripe"
    assert len(client.get("/providers/").json()) == 1


def test_duplicate_provider_returns_409(client: TestClient) -> None:
    create_provider(client)

    assert client.post("/providers/", json=PROVIDER_BODY).status_code == 409


def test_missing_provider_returns_404(client: TestClient) -> None:
    assert client.get("/providers/99").status_code == 404


def test_subscription_flow(client: TestClient) -> None:
    provider_id = create_provider(client)
    body = {"email": "a@b.com", "provider_id": provider_id}

    created = client.post("/subscriptions/", json=body)
    assert created.status_code == 201
    assert client.post("/subscriptions/", json=body).status_code == 409
    assert len(client.get("/subscriptions/", params={"email": "a@b.com"}).json()) == 1

    assert client.delete(f"/subscriptions/{created.json()['id']}").status_code == 204
    assert client.delete(f"/subscriptions/{created.json()['id']}").status_code == 404


def test_subscription_validates_email_and_provider(client: TestClient) -> None:
    provider_id = create_provider(client)

    assert client.post("/subscriptions/", json={"email": "nope", "provider_id": provider_id}).status_code == 422
    assert client.post("/subscriptions/", json={"email": "a@b.com", "provider_id": 99}).status_code == 404


def test_changelog_refresh_and_breaking_filter(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    provider_id = create_provider(client)
    entries = [
        make_fetched("v2.0", "https://example.com/v2", "Removed the client_id field"),
        make_fetched("v1.1", "https://example.com/v1.1", "Improved error messages"),
    ]

    def fake_fetch(self: FeedChangelogFetcher, url: str) -> list[FetchedEntryInput]:
        return entries

    monkeypatch.setattr(FeedChangelogFetcher, "fetch", fake_fetch)

    refreshed = client.post(f"/changelog/{provider_id}/refresh").json()
    assert len(refreshed) == 2
    assert client.post(f"/changelog/{provider_id}/refresh").json() == []
    assert len(client.get(f"/changelog/{provider_id}").json()) == 2

    breaking = client.get(f"/changelog/{provider_id}", params={"breaking_only": True}).json()
    assert [e["title"] for e in breaking] == ["v2.0"]


def test_changelog_for_unknown_provider_returns_404(client: TestClient) -> None:
    assert client.get("/changelog/99").status_code == 404
