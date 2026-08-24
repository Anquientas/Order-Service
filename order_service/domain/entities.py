import datetime
from dataclasses import dataclass

from order_service.constants.order import OrderStatus


@dataclass(slots=True)
class Order:
    id: str
    user_id: str
    item_id: str
    quantity: int
    status: OrderStatus
    idempotency_key: str | None
    created_at: datetime.datetime | None = None
    updated_at: datetime.datetime | None = None


@dataclass(slots=True)
class CatalogItem:
    id: str
    available_qty: int
