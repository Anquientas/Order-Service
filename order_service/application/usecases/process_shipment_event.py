from order_service.application.ports.unit_of_work import UnitOfWork
from order_service.constants.kafka import SHIPMENT_EVENT_TO_ORDER_STATUS
from order_service.constants.notification import (
    DefaultCancellationReason,
    NotificationIdempotencyKey,
    NotificationMessage,
)
from order_service.constants.order import OrderStatus
from order_service.domain.entities import NotificationOutboxRecord


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
        reason: str | None = None,
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
                    await self._uow.orders.update_status(
                        order_id, new_status
                    )
                    await self._enqueue_notification(
                        order_id, new_status, reason
                    )

            await self._uow.inbox.mark_processed(topic, partition, offset)
            await self._uow.commit()

    async def _enqueue_notification(
        self,
        order_id: str,
        new_status: OrderStatus,
        reason: str | None,
    ) -> None:
        if new_status == OrderStatus.shipped:
            record = NotificationOutboxRecord(
                id=NotificationIdempotencyKey.order_shipped.format(
                    order_id=order_id
                ),
                message=NotificationMessage.order_shipped,
                reference_id=order_id,
            )
        elif new_status == OrderStatus.cancelled:
            record = NotificationOutboxRecord(
                id=NotificationIdempotencyKey.order_cancelled.format(
                    order_id=order_id
                ),
                message=NotificationMessage.order_cancelled.format(
                    reason=reason
                    or DefaultCancellationReason.shipment_cancelled
                ),
                reference_id=order_id,
            )
        else:
            return
        await self._uow.notification_outbox.enqueue(record)
