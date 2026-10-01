from app.core.exceptions import NotFoundError
from app.domain.entities.changelog_entry_entity import ChangelogEntryEntity
from app.domain.entities.provider_entity import ProviderEntity
from app.domain.fetchers.changelog_fetcher import ChangelogFetcher
from app.domain.inputs.changelog_entry_input import CreateChangelogEntryInput
from app.domain.repos.changelog_entry_repo import ChangelogEntryRepo
from app.domain.repos.provider_repo import ProviderRepo
from app.domain.services.breaking_change_classifier import BreakingChangeClassifier


class ChangelogUsecase:
    def __init__(
        self,
        repo: ChangelogEntryRepo,
        provider_repo: ProviderRepo,
        fetcher: ChangelogFetcher,
        classifier: BreakingChangeClassifier,
    ) -> None:
        self.repo = repo
        self.provider_repo = provider_repo
        self.fetcher = fetcher
        self.classifier = classifier

    def list_entries(self, provider_id: int, breaking_only: bool = False) -> list[ChangelogEntryEntity]:
        self._get_provider(provider_id)
        return self.repo.get_by_provider(provider_id, breaking_only)

    def refresh(self, provider_id: int) -> list[ChangelogEntryEntity]:
        provider = self._get_provider(provider_id)
        known_urls = self.repo.get_urls_by_provider(provider_id)
        new_entries = []
        for fetched in self.fetcher.fetch(provider.changelog_url):
            if not fetched.url or fetched.url in known_urls:
                continue
            known_urls.add(fetched.url)
            is_breaking = self.classifier.is_breaking(fetched.title, fetched.summary)
            data = CreateChangelogEntryInput(provider_id=provider_id, is_breaking=is_breaking, **fetched.model_dump())
            new_entries.append(self.repo.create(data))
        return new_entries

    def _get_provider(self, provider_id: int) -> ProviderEntity:
        provider = self.provider_repo.get_by_id(provider_id)
        if provider is None:
            raise NotFoundError("Provider not found")
        return provider
