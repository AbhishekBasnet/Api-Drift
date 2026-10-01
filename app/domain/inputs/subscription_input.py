from pydantic import BaseModel


class CreateSubscriptionInput(BaseModel):
    email: str
    provider_id: int
