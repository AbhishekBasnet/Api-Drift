from abc import ABC, abstractmethod

from app.domain.inputs.changelog_entry_input import FetchedEntryInput


class ChangelogFetcher(ABC):
    @abstractmethod
    def fetch(self, url: str) -> list[FetchedEntryInput]: ...
