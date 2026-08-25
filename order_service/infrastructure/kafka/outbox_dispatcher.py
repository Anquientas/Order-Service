import asyncio
import contextlib
import logging
from collections.abc import Callable

from order_service.application.ports.event_publisher import EventPublisher
from order_service.application.ports.unit_of_work import UnitOfWork
from order_service.constants.kafka import EventTopic
from order_service.constants.log_messages import OutboxDispatcherLogMessage

logger = logging.getLogger(__name__)


class OutboxDispatcher:
    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        publisher: EventPublisher,
        interval_seconds: float = 5.0,
        max_attempts: int = 5,
        batch_limit: int = 50,
    ) -> None:
        self._uow_factory = uow_factory
        self._publisher = publisher
        self._interval_seconds = interval_seconds
        self._max_attempts = max_attempts
        self._batch_limit = batch_limit
        self._task: asyncio.Task | None = None
        self._stopping = asyncio.Event()

    def start(self) -> None:
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._stopping.set()
        if self._task is not None:
            await self._task

    async def _run(self) -> None:
        while not self._stopping.is_set():
            try:
                await self._dispatch_once()
            except Exception:
                logger.exception(
                    OutboxDispatcherLogMessage.dispatch_cycle_failed
                )
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(
                    self._stopping.wait(), timeout=self._interval_seconds
                )

    async def _dispatch_once(self) -> None:
        uow: UnitOfWork = self._uow_factory()
        async with uow:
            records = await uow.outbox.get_pending(self._batch_limit)
            for record in records:
                try:
                    await self._publisher.publish(
                        EventTopic.order,
                        record.payload,
                        key=record.payload.get('order_id'),
                    )
                    await uow.outbox.mark_sent(record.id)
                except Exception as exception:
                    if record.attempts_number + 1 >= self._max_attempts:
                        await uow.outbox.mark_permanently_failed(
                            record.id, str(exception)
                        )
                        logger.error(
                            OutboxDispatcherLogMessage.permanently_failed,
                            record.id,
                            record.attempts_number + 1,
                            exception,
                        )
                    else:
                        await uow.outbox.mark_retry(record.id, str(exception))
                        logger.warning(
                            OutboxDispatcherLogMessage.retry_attempt_failed,
                            record.id,
                            record.attempts_number + 1,
                            exception,
                        )
            await uow.commit()
