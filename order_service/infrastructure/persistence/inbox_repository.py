from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from order_service.infrastructure.persistence.models import InboxModel


class SqlAlchemyInboxRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def is_processed(
        self, topic: str, partition: int, offset: int
    ) -> bool:
        statement = select(InboxModel.id).where(
            InboxModel.topic == topic,
            InboxModel.partition == partition,
            InboxModel.offset == offset,
        )
        row = (await self._session.execute(statement)).scalar_one_or_none()
        return row is not None

    async def mark_processed(
        self, topic: str, partition: int, offset: int
    ) -> None:
        model = InboxModel(
            id=f'{topic}:{partition}:{offset}',
            topic=topic,
            partition=partition,
            offset=offset,
        )
        try:
            async with self._session.begin_nested():
                self._session.add(model)
                await self._session.flush()
        except IntegrityError:
            pass
