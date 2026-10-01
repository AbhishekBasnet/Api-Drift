from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SubscriptionModel(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (UniqueConstraint("email", "provider_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255))
    provider_id: Mapped[int] = mapped_column(ForeignKey("providers.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
