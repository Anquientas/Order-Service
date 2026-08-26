from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from order_service.constants.outbox import OutboxStatus
from order_service.domain.entities import OutboxRecord
from order_service.infrastructure.persistence.models import OutboxModel


def _to_domain(row: OutboxModel) -> OutboxRecord:
    return OutboxRecord(
        id=row.id,
        event_type=row.event_type,
        payload=row.payload,
        status=OutboxStatus(row.status),
        attempts_number=row.attempts_number,
        error=row.error,
        created_at=row.created_at,
        changed_at=row.changed_at,
    )


class SqlAlchemyOutboxRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def enqueue(self, record: OutboxRecord) -> None:
        self._session.add(
            OutboxModel(
                id=record.id,
                event_type=record.event_type,
                payload=record.payload,
                status=record.status,
                attempts_number=record.attempts_number,
                error=record.error,
            )
        )

    async def get_pending(self, limit: int) -> list[OutboxRecord]:
        statement = (
            select(OutboxModel)
            .where(OutboxModel.status == OutboxStatus.pending)
            .order_by(OutboxModel.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        rows = (await self._session.execute(statement)).scalars().all()
        return [_to_domain(row) for row in rows]

    async def mark_sent(self, record_id: str) -> None:
        model = await self._session.get(OutboxModel, record_id)
        if model is not None:
            model.status = OutboxStatus.sent

    async def mark_retry(self, record_id: str, error: str) -> None:
        model = await self._session.get(OutboxModel, record_id)
        if model is not None:
            model.attempts_number += 1
            model.error = error[:1024]

    async def mark_permanently_failed(
        self, record_id: str, error: str
    ) -> None:
        model = await self._session.get(OutboxModel, record_id)
        if model is not None:
            model.status = OutboxStatus.failed
            model.attempts_number += 1
            model.error = error[:1024]
