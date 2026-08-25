from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from order_service.infrastructure.persistence.inbox_repository import (
    SqlAlchemyInboxRepository,
)
from order_service.infrastructure.persistence.notification_repository import (
    SqlAlchemyNotificationOutboxRepository,
)
from order_service.infrastructure.persistence.order_repository import (
    SqlAlchemyOrderRepository,
)
from order_service.infrastructure.persistence.outbox_repository import (
    SqlAlchemyOutboxRepository,
)


class SqlAlchemyUnitOfWork:
    def __init__(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> 'SqlAlchemyUnitOfWork':
        self._session = self._session_factory()
        self.orders = SqlAlchemyOrderRepository(self._session)
        self.outbox = SqlAlchemyOutboxRepository(self._session)
        self.inbox = SqlAlchemyInboxRepository(self._session)
        self.notification_outbox = SqlAlchemyNotificationOutboxRepository(
            self._session
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        assert self._session is not None
        try:
            if exc_type is not None:
                await self._session.rollback()
        finally:
            await self._session.close()
            self._session = None

    async def commit(self) -> None:
        assert self._session is not None
        await self._session.commit()

    async def rollback(self) -> None:
        assert self._session is not None
        await self._session.rollback()
