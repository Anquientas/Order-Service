from order_service.application.usecases.process_shipment_event import (
    ProcessShipmentEventUsecase,
)
from order_service.infrastructure.kafka.consumer import (
    ShipmentEventsConsumer,
)
from order_service.infrastructure.kafka.outbox_dispatcher import (
    OutboxDispatcher,
)
from order_service.infrastructure.kafka.producer import KafkaEventPublisher
from order_service.infrastructure.persistence.database import SessionFactory
from order_service.infrastructure.persistence.unit_of_work import (
    SqlAlchemyUnitOfWork,
)
from order_service.settings import settings

_event_publisher = KafkaEventPublisher(
    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
)

_outbox_dispatcher = OutboxDispatcher(
    uow_factory=lambda: SqlAlchemyUnitOfWork(SessionFactory),
    publisher=_event_publisher,
    interval_seconds=settings.OUTBOX_DISPATCH_INTERVAL_SECONDS,
    max_attempts=settings.OUTBOX_MAX_ATTEMPTS,
    batch_limit=settings.OUTBOX_BATCH_LIMIT,
)

_shipment_events_consumer = ShipmentEventsConsumer(
    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    usecase_factory=lambda: ProcessShipmentEventUsecase(
        SqlAlchemyUnitOfWork(SessionFactory)
    ),
    group_id=settings.KAFKA_CONSUMER_GROUP_ID,
)


async def start_background_workers() -> None:
    await _event_publisher.start()
    _outbox_dispatcher.start()
    await _shipment_events_consumer.start()


async def stop_background_workers() -> None:
    await _shipment_events_consumer.stop()
    await _outbox_dispatcher.stop()
    await _event_publisher.stop()
