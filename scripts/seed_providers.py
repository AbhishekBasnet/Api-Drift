from app.core.database import SessionLocal
from app.core.exceptions import AlreadyExistsError
from app.domain.inputs.provider_input import CreateProviderInput
from app.infra.repos.db_provider_repo import DbProviderRepo
from app.usecases.provider_usecase import ProviderUsecase

SEED_PROVIDERS = [
    CreateProviderInput(
        name="Stripe", slug="stripe", changelog_url="https://github.com/stripe/stripe-python/releases.atom"
    ),
    CreateProviderInput(
        name="Twilio", slug="twilio", changelog_url="https://github.com/twilio/twilio-python/releases.atom"
    ),
    CreateProviderInput(
        name="OpenAI", slug="openai", changelog_url="https://github.com/openai/openai-python/releases.atom"
    ),
    CreateProviderInput(name="GitHub", slug="github", changelog_url="https://github.blog/changelog/feed/"),
    CreateProviderInput(
        name="Anthropic",
        slug="anthropic",
        changelog_url="https://github.com/anthropics/anthropic-sdk-python/releases.atom",
    ),
    CreateProviderInput(
        name="Slack", slug="slack", changelog_url="https://github.com/slackapi/python-slack-sdk/releases.atom"
    ),
    CreateProviderInput(
        name="SendGrid", slug="sendgrid", changelog_url="https://github.com/sendgrid/sendgrid-python/releases.atom"
    ),
]


def seed_providers(usecase: ProviderUsecase) -> tuple[int, int]:
    created = 0
    skipped = 0
    for provider in SEED_PROVIDERS:
        try:
            usecase.create_provider(provider)
            created += 1
        except AlreadyExistsError:
            skipped += 1
    return created, skipped


def main() -> None:
    db = SessionLocal()
    try:
        created, skipped = seed_providers(ProviderUsecase(DbProviderRepo(db)))
    finally:
        db.close()
    print(f"Seeded providers: {created} created, {skipped} already existed")


if __name__ == "__main__":
    main()
