import uuid

from order_service.application.ports.catalog_client import CatalogClient
from order_service.application.ports.unit_of_work import UnitOfWork
from order_service.domain.entities import Order, OrderStatus
from order_service.domain.exceptions import InsufficientStock, ItemNotFound


class CreateOrderUsecase:
    def __init__(self, uow: UnitOfWork, catalog: CatalogClient) -> None:
        self._uow = uow
        self._catalog = catalog

    async def execute(
        self,
        user_id: str,
        item_id: str,
        quantity: int,
        idempotency_key: str | None,
    ) -> Order:
        async with self._uow:
            if idempotency_key:
                existing = await self._uow.orders.get_by_idempotency_key(
                    idempotency_key=idempotency_key
                )
                if existing is not None:
                    return existing

            item = await self._catalog.get_item(item_id)
            if item is None:
                raise ItemNotFound(item_id)
            if item.available_qty < quantity:
                raise InsufficientStock(
                    item_id=item_id,
                    requested=quantity,
                    available=item.available_qty,
                )

            order = Order(
                id=str(uuid.uuid4()),
                user_id=user_id,
                item_id=item_id,
                quantity=quantity,
                status=OrderStatus.new,
                idempotency_key=idempotency_key,
            )
            await self._uow.orders.add(order)
            await self._uow.commit()
            return order
