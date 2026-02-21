"""Merchant activity event model."""
from decimal import Decimal
from uuid import UUID
from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from src.db.base import Base


class Activity(Base):
    """Merchant activity event from CSV logs."""

    __tablename__ = "merchant_activities"

    event_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    event_timestamp: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    product: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(32), nullable=True)
    region: Mapped[str] = mapped_column(String(64), nullable=True)
    merchant_tier: Mapped[str] = mapped_column(String(32), nullable=True)

