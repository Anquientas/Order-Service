import asyncio
import json
import logging
from collections.abc import Callable

from aiokafka import AIOKafkaConsumer
from aiokafka.structs import ConsumerRecord

from order_service.application.usecases.process_shipment_event import (
    ProcessShipmentEventUsecase,
)
from order_service.constants.kafka import EventTopic
from order_service.constants.log_messages import ShipmentConsumerLogMessage

logger = logging.getLogger(__name__)


class ShipmentEventsConsumer:
    def __init__(
        self,
        bootstrap_servers: str,
        usecase_factory: Callable[[], ProcessShipmentEventUsecase],
        group_id: str = 'order-service',
    ) -> None:
        self._bootstrap_servers = bootstrap_servers
        self._group_id = group_id
        self._usecase_factory = usecase_factory
        self._consumer: AIOKafkaConsumer | None = None
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        self._consumer = AIOKafkaConsumer(
            EventTopic.shipment,
            bootstrap_servers=self._bootstrap_servers,
            group_id=self._group_id,
            enable_auto_commit=False,
        )
        await self._consumer.start()
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
        if self._consumer is not None:
            await self._consumer.stop()
            self._consumer = None

    async def _run(self) -> None:
        assert self._consumer is not None
        async for message in self._consumer:
            await self._handle_message(message)

    async def _handle_message(self, message: ConsumerRecord) -> None:
        try:
            data = json.loads(message.value)
            usecase = self._usecase_factory()
            await usecase.execute(
                topic=message.topic,
                partition=message.partition,
                offset=message.offset,
                event_type=data.get('event_type'),
                order_id=data.get('order_id'),
                reason=data.get('reason'),
            )
        except Exception:
            logger.exception(
                ShipmentConsumerLogMessage.processing_failed,
                message.topic,
                message.partition,
                message.offset,
            )
            return
        await self._consumer.commit()
