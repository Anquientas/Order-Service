import uuid
from decimal import Decimal

from order_service.application.ports.catalog_client import CatalogClient
from order_service.application.ports.payments_client import PaymentsClient
from order_service.application.ports.unit_of_work import UnitOfWork
from order_service.constants.notification import (
    DefaultCancellationReason,
    NotificationIdempotencyKey,
    NotificationMessage,
)
from order_service.constants.order import OrderStatus
from order_service.domain.entities import NotificationOutboxRecord, Order
from order_service.domain.exceptions import (
    DuplicateIdempotencyKey,
    InsufficientStock,
    ItemNotFound,
)


class CreateOrderUsecase:
    def __init__(
        self,
        uow: UnitOfWork,
        catalog: CatalogClient,
        payments: PaymentsClient,
        callback_url: str,
    ) -> None:
        self._uow = uow
        self._catalog = catalog
        self._payments = payments
        self._callback_url = callback_url

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
                    idempotency_key
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
            try:
                order = await self._uow.orders.add(order)
            except DuplicateIdempotencyKey:
                assert idempotency_key is not None
                winner = await self._uow.orders.get_by_idempotency_key(
                    idempotency_key
                )
                if winner is None:
                    raise
                return winner

            amount = (item.price * quantity).quantize(Decimal('0.01'))
            payment = await self._payments.create_payment(
                order_id=order.id,
                amount=str(amount),
                callback_url=self._callback_url,
                idempotency_key=str(uuid.uuid4()),
            )
            if payment is None:
                order.status = OrderStatus.cancelled
                await self._uow.orders.update_status(
                    order.id, OrderStatus.cancelled
                )
                await self._uow.notification_outbox.enqueue(
                    NotificationOutboxRecord(
                        id=NotificationIdempotencyKey.order_cancelled.format(
                            order_id=order.id
                        ),
                        message=NotificationMessage.order_cancelled.format(
                            reason=DefaultCancellationReason.payment_not_created
                        ),
                        reference_id=order.id,
                    )
                )
            else:
                order.payment_id = payment.id
                await self._uow.orders.set_payment_id(order.id, payment.id)
                await self._uow.notification_outbox.enqueue(
                    NotificationOutboxRecord(
                        id=NotificationIdempotencyKey.order_new.format(
                            order_id=order.id
                        ),
                        message=NotificationMessage.order_new,
                        reference_id=order.id,
                    )
                )

            await self._uow.commit()
            return order
