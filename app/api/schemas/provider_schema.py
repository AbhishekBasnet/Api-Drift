from datetime import datetime

from pydantic import BaseModel


class ProviderCreateRequest(BaseModel):
    name: str
    slug: str
    changelog_url: str


class ProviderResponse(BaseModel):
    id: int
    name: str
    slug: str
    changelog_url: str
    created_at: datetime
