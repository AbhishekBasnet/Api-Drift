from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SubscriptionEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    provider_id: int
    created_at: datetime
