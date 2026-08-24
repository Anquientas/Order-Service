import datetime
from dataclasses import dataclass
from decimal import Decimal

from order_service.constants.order import OrderStatus


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
