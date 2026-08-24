from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from order_service.domain.entities import Order, OrderStatus
from order_service.domain.exceptions import DuplicateIdempotencyKey
from order_service.infrastructure.persistence.models import OrderModel


def _to_domain(row: OrderModel) -> Order:
    return Order(
        id=row.id,
        user_id=row.user_id,
        item_id=row.item_id,
        quantity=row.quantity,
        status=OrderStatus(row.status),
        idempotency_key=row.idempotency_key,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class SqlAlchemyOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, order: Order) -> Order:
        model = OrderModel(
            id=order.id,
            user_id=order.user_id,
            item_id=order.item_id,
            quantity=order.quantity,
            status=order.status,
            idempotency_key=order.idempotency_key,
        )
        try:
            async with self._session.begin_nested():
                self._session.add(model)
                await self._session.flush()
        except IntegrityError as exception:
            assert order.idempotency_key is not None
            raise DuplicateIdempotencyKey(
                order.idempotency_key
            ) from exception
        return _to_domain(model)

    async def get(self, order_id: str) -> Order | None:
        row = await self._session.get(OrderModel, order_id)
        return _to_domain(row) if row else None

    async def get_by_idempotency_key(self, key: str) -> Order | None:
        statement = select(OrderModel).where(
            OrderModel.idempotency_key == key
        )
        row = (await self._session.execute(statement)).scalar_one_or_none()
        return _to_domain(row) if row else None
