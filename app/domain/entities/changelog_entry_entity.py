from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChangelogEntryEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    provider_id: int
    title: str
    url: str
    summary: str
    published_at: datetime
    is_breaking: bool
    created_at: datetime
