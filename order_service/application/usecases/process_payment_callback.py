from order_service.application.ports.unit_of_work import UnitOfWork
from order_service.constants.order import OrderStatus
from order_service.constants.payment import PaymentStatus


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

            new_status = (
                OrderStatus.paid
                if status == PaymentStatus.succeeded
                else OrderStatus.cancelled
            )
            await self._uow.orders.update_status(order_id, new_status)
            await self._uow.commit()
