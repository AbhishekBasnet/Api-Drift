from pydantic import BaseModel


class CreateProviderInput(BaseModel):
    name: str
    slug: str
    changelog_url: str
