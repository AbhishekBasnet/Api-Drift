from datetime import datetime

from pydantic import BaseModel


class ChangelogEntryResponse(BaseModel):
    id: int
    provider_id: int
    title: str
    url: str
    summary: str
    published_at: datetime
    created_at: datetime
