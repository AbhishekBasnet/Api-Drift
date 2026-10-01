import httpx
import pytest

from app.core.exceptions import FetchError
from app.infra.clients.feed_changelog_fetcher import FeedChangelogFetcher

URL = "https://example.com/feed"

ATOM = b"""<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title> v2.0 </title>
    <link href="https://example.com/v2"/>
    <updated>2026-09-30T10:00:00Z</updated>
    <content type="html">&lt;p&gt;Removed the client_id field&lt;/p&gt;</content>
  </entry>
</feed>"""

RSS = b"""<?xml version="1.0"?>
<rss version="2.0"><channel>
  <item>
    <title>Version 3</title>
    <link>https://example.com/v3</link>
    <pubDate>Tue, 29 Sep 2026 08:00:00 GMT</pubDate>
    <description>New endpoint</description>
  </item>
</channel></rss>"""


def serve(monkeypatch: pytest.MonkeyPatch, content: bytes, status_code: int = 200) -> None:
    def fake_get(url: str, **kwargs: object) -> httpx.Response:
        return httpx.Response(status_code, content=content, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx, "get", fake_get)


def test_parses_atom_feed(monkeypatch: pytest.MonkeyPatch) -> None:
    serve(monkeypatch, ATOM)

    [entry] = FeedChangelogFetcher().fetch(URL)

    assert entry.title == "v2.0"
    assert entry.url == "https://example.com/v2"
    assert entry.summary == "<p>Removed the client_id field</p>"
    assert entry.published_at.year == 2026
    assert entry.published_at.tzinfo is not None


def test_parses_rss_feed(monkeypatch: pytest.MonkeyPatch) -> None:
    serve(monkeypatch, RSS)

    [entry] = FeedChangelogFetcher().fetch(URL)

    assert entry.title == "Version 3"
    assert entry.url == "https://example.com/v3"
    assert entry.summary == "New endpoint"
    assert entry.published_at.day == 29


def test_http_error_raises_fetch_error(monkeypatch: pytest.MonkeyPatch) -> None:
    serve(monkeypatch, b"", status_code=500)

    with pytest.raises(FetchError):
        FeedChangelogFetcher().fetch(URL)


def test_invalid_xml_raises_fetch_error(monkeypatch: pytest.MonkeyPatch) -> None:
    serve(monkeypatch, b"<html>not a feed")

    with pytest.raises(FetchError):
        FeedChangelogFetcher().fetch(URL)


def test_entity_expansion_attack_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    bomb = b'<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "aaaa"><!ENTITY b "&a;&a;&a;&a;">]><rss><x>&b;</x></rss>'
    serve(monkeypatch, bomb)

    with pytest.raises(FetchError):
        FeedChangelogFetcher().fetch(URL)


def test_atom_entry_with_missing_fields_uses_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    serve(monkeypatch, b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Bare</title></entry></feed>')

    [entry] = FeedChangelogFetcher().fetch(URL)

    assert entry.url == ""
    assert entry.summary == ""
    assert entry.published_at.tzinfo is not None


def test_long_summary_is_truncated(monkeypatch: pytest.MonkeyPatch) -> None:
    long_text = "x" * 5000
    serve(
        monkeypatch,
        f"<rss><channel><item><title>t</title><description>{long_text}</description></item></channel></rss>".encode(),
    )

    [entry] = FeedChangelogFetcher().fetch(URL)

    assert len(entry.summary) == 2000


@pytest.mark.parametrize("date", ["not a date", "", "32 Foo 2026"])
def test_unparseable_dates_fall_back_to_now(date: str) -> None:
    parsed = FeedChangelogFetcher._parse_date(date)

    assert parsed.tzinfo is not None
    assert parsed.year >= 2026


def test_naive_iso_date_is_assumed_utc() -> None:
    parsed = FeedChangelogFetcher._parse_date("2026-09-30T10:00:00")

    assert parsed.utcoffset() is not None
    assert parsed.utcoffset().total_seconds() == 0
