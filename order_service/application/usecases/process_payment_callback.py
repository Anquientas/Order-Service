import uuid

from order_service.application.ports.unit_of_work import UnitOfWork
from order_service.constants.kafka import OrderEventType
from order_service.constants.order import OrderStatus
from order_service.constants.outbox import OutboxStatus
from order_service.constants.payment import PaymentStatus
from order_service.domain.entities import OutboxRecord


class ProcessPaymentCallbackUsecase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        order_id: str,
        payment_id: str,
        status: PaymentStatus,
    ) -> None:
        async with self._uow:
            order = await self._uow.orders.get(order_id)
            if order is None:
                return

            if order.status in (OrderStatus.paid, OrderStatus.cancelled):
                return

            if (
                order.payment_id is not None
                and order.payment_id != payment_id
            ):
                return

            if status == PaymentStatus.succeeded:
                await self._uow.orders.update_status(
                    order_id, OrderStatus.paid
                )
                assert order.payment_id is not None
                await self._uow.outbox.enqueue(
                    OutboxRecord(
                        id=str(uuid.uuid4()),
                        event_type=OrderEventType.paid,
                        payload={
                            'event_type': OrderEventType.paid,
                            'order_id': order.id,
                            'item_id': order.item_id,
                            'quantity': order.quantity,
                            'idempotency_key': order.payment_id,
                        },
                        status=OutboxStatus.pending,
                    )
                )
            else:
                await self._uow.orders.update_status(
                    order_id, OrderStatus.cancelled
                )

            await self._uow.commit()
