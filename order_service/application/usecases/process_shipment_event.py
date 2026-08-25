from order_service.application.ports.unit_of_work import UnitOfWork
from order_service.constants.kafka import SHIPMENT_EVENT_TO_ORDER_STATUS
from order_service.constants.order import OrderStatus


class ProcessShipmentEventUsecase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        topic: str,
        partition: int,
        offset: int,
        event_type: str | None,
        order_id: str | None,
    ) -> None:
        async with self._uow:
            if await self._uow.inbox.is_processed(topic, partition, offset):
                return

            new_status = SHIPMENT_EVENT_TO_ORDER_STATUS.get(event_type)
            if new_status is not None and order_id is not None:
                order = await self._uow.orders.get(order_id)
                if order is not None and order.status not in (
                    OrderStatus.shipped,
                    OrderStatus.cancelled,
                ):
                    await self._uow.orders.update_status(order_id, new_status)

            await self._uow.inbox.mark_processed(topic, partition, offset)
            await self._uow.commit()
