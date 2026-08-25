import datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    DateTime,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from order_service.infrastructure.persistence.database import Base


def _utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


class OrderModel(Base):
    __tablename__ = 'orders'

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64))
    item_id: Mapped[str] = mapped_column(String(64))
    quantity: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(16))
    idempotency_key: Mapped[str | None] = mapped_column(
        String(128), nullable=True, unique=True
    )
    payment_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )


class OutboxModel(Base):
    __tablename__ = 'outbox'

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(16))
    attempts_number: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    changed_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )


class InboxModel(Base):
    __tablename__ = 'inbox'
    __table_args__ = (
        UniqueConstraint(
            'topic', 'partition', 'offset', name='uq_inbox_message'
        ),
    )

    id: Mapped[str] = mapped_column(String(96), primary_key=True)
    topic: Mapped[str] = mapped_column(String(128))
    partition: Mapped[int] = mapped_column(Integer)
    offset: Mapped[int] = mapped_column(BigInteger)
    processed_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )


class NotificationOutboxModel(Base):
    __tablename__ = 'notification_outbox'

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    message: Mapped[str] = mapped_column(String(1024))
    reference_id: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(16))
    attempts_number: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    changed_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )
