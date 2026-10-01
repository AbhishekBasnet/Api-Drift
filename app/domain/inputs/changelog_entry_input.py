from datetime import datetime

from pydantic import BaseModel


class FetchedEntryInput(BaseModel):
    title: str
    url: str
    summary: str
    published_at: datetime


class CreateChangelogEntryInput(FetchedEntryInput):
    provider_id: int
