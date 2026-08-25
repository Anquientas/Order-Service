import datetime
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from order_service.constants.order import OrderStatus
from order_service.constants.outbox import OutboxStatus


@dataclass(slots=True)
class Order:
    id: str
    user_id: str
    item_id: str
    quantity: int
    status: OrderStatus
    idempotency_key: str | None
    payment_id: str | None = None
    created_at: datetime.datetime | None = None
    updated_at: datetime.datetime | None = None


@dataclass(slots=True)
class CatalogItem:
    id: str
    available_qty: int
    price: Decimal


@dataclass(slots=True)
class Payment:
    id: str
    order_id: str
    status: str


@dataclass(slots=True)
class OutboxRecord:
    id: str
    event_type: str
    payload: dict[str, Any]
    status: OutboxStatus = OutboxStatus.pending
    attempts_number: int = 0
    error: str | None = None
    created_at: datetime.datetime | None = None
    changed_at: datetime.datetime | None = None


@dataclass(slots=True)
class NotificationOutboxRecord:
    id: str
    message: str
    reference_id: str
    status: OutboxStatus = OutboxStatus.pending
    attempts_number: int = 0
    error: str | None = None
    created_at: datetime.datetime | None = None
    changed_at: datetime.datetime | None = None
