from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProviderEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    changelog_url: str
    created_at: datetime
