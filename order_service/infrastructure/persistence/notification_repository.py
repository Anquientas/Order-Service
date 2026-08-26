from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from order_service.constants.outbox import OutboxStatus
from order_service.domain.entities import NotificationOutboxRecord
from order_service.infrastructure.persistence.models import (
    NotificationOutboxModel,
)


def _to_domain(row: NotificationOutboxModel) -> NotificationOutboxRecord:
    return NotificationOutboxRecord(
        id=row.id,
        message=row.message,
        reference_id=row.reference_id,
        status=OutboxStatus(row.status),
        attempts_number=row.attempts_number,
        error=row.error,
        created_at=row.created_at,
        changed_at=row.changed_at,
    )


class SqlAlchemyNotificationOutboxRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def enqueue(self, record: NotificationOutboxRecord) -> None:
        model = NotificationOutboxModel(
            id=record.id,
            message=record.message,
            reference_id=record.reference_id,
            status=record.status,
            attempts_number=record.attempts_number,
            error=record.error,
        )
        try:
            async with self._session.begin_nested():
                self._session.add(model)
                await self._session.flush()
        except IntegrityError:
            pass

    async def get_pending(self, limit: int) -> list[NotificationOutboxRecord]:
        statement = (
            select(NotificationOutboxModel)
            .where(NotificationOutboxModel.status == OutboxStatus.pending)
            .order_by(NotificationOutboxModel.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        rows = (await self._session.execute(statement)).scalars().all()
        return [_to_domain(row) for row in rows]

    async def mark_sent(self, record_id: str) -> None:
        model = await self._session.get(NotificationOutboxModel, record_id)
        if model is not None:
            model.status = OutboxStatus.sent

    async def mark_retry(self, record_id: str, error: str) -> None:
        model = await self._session.get(NotificationOutboxModel, record_id)
        if model is not None:
            model.attempts_number += 1
            model.error = error[:1024]

    async def mark_permanently_failed(
        self, record_id: str, error: str
    ) -> None:
        model = await self._session.get(NotificationOutboxModel, record_id)
        if model is not None:
            model.status = OutboxStatus.failed
            model.attempts_number += 1
            model.error = error[:1024]
