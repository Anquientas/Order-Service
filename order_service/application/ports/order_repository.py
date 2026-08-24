from typing import Protocol

from order_service.constants.order import OrderStatus
from order_service.domain.entities import Order


class OrderRepository(Protocol):
    async def add(self, order: Order) -> Order: ...

    async def get(self, order_id: str) -> Order | None: ...

    async def get_by_idempotency_key(
        self, idempotency_key: str
    ) -> Order | None: ...

    async def update_status(
        self, order_id: str, status: OrderStatus
    ) -> None: ...

    async def set_payment_id(
        self, order_id: str, payment_id: str
    ) -> None: ...
