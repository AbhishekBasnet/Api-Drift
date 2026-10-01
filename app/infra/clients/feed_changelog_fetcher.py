from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import override
from xml.etree.ElementTree import Element

import httpx
from defusedxml import ElementTree
from defusedxml.common import DefusedXmlException

from app.core.exceptions import FetchError
from app.domain.fetchers.changelog_fetcher import ChangelogFetcher
from app.domain.inputs.changelog_entry_input import FetchedEntryInput

ATOM = "{http://www.w3.org/2005/Atom}"
MAX_SUMMARY_LENGTH = 2000


class FeedChangelogFetcher(ChangelogFetcher):
    @override
    def fetch(self, url: str) -> list[FetchedEntryInput]:
        try:
            response = httpx.get(url, timeout=10, follow_redirects=True)
            response.raise_for_status()
            root = ElementTree.fromstring(response.content)
        except (httpx.HTTPError, ElementTree.ParseError, DefusedXmlException) as exc:
            raise FetchError(f"Could not fetch changelog from {url}") from exc

        if root.tag == f"{ATOM}feed":
            return [self._parse_atom_entry(entry) for entry in root.findall(f"{ATOM}entry")]
        return [self._parse_rss_item(item) for item in root.iter("item")]

    def _parse_atom_entry(self, entry: Element) -> FetchedEntryInput:
        link = entry.find(f"{ATOM}link")
        body = entry.findtext(f"{ATOM}content") or entry.findtext(f"{ATOM}summary") or ""
        date = entry.findtext(f"{ATOM}updated") or entry.findtext(f"{ATOM}published")
        return FetchedEntryInput(
            title=(entry.findtext(f"{ATOM}title") or "").strip(),
            url=link.get("href", "") if link is not None else "",
            summary=body.strip()[:MAX_SUMMARY_LENGTH],
            published_at=self._parse_date(date),
        )

    def _parse_rss_item(self, item: Element) -> FetchedEntryInput:
        return FetchedEntryInput(
            title=(item.findtext("title") or "").strip(),
            url=(item.findtext("link") or "").strip(),
            summary=(item.findtext("description") or "").strip()[:MAX_SUMMARY_LENGTH],
            published_at=self._parse_date(item.findtext("pubDate")),
        )

    @staticmethod
    def _parse_date(value: str | None) -> datetime:
        if not value:
            return datetime.now(UTC)
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            try:
                parsed = parsedate_to_datetime(value)
            except TypeError, ValueError:
                return datetime.now(UTC)
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
