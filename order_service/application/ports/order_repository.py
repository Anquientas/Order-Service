from typing import Protocol

from order_service.domain.entities import Order


class OrderRepository(Protocol):
    """Интерфейс хранения заказов."""

    async def add(self, order: Order) -> None: ...

    async def get(self, order_id: str) -> Order | None: ...

    async def get_by_idempotency_key(
        self, idempotency_key: str
    ) -> Order | None: ...
