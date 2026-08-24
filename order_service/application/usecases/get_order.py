from order_service.application.ports.unit_of_work import UnitOfWork
from order_service.domain.entities import Order
from order_service.domain.exceptions import OrderNotFound


class GetOrderUsecase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, order_id: str) -> Order:
        async with self._uow:
            order = await self._uow.orders.get(order_id)
            if order is None:
                raise OrderNotFound(order_id)
            return order
