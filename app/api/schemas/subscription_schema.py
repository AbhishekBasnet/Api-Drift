from datetime import datetime

from pydantic import BaseModel, EmailStr


class SubscriptionCreateRequest(BaseModel):
    email: EmailStr
    provider_id: int


class SubscriptionResponse(BaseModel):
    id: int
    email: str
    provider_id: int
    created_at: datetime
