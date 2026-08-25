from order_service.application.usecases.process_shipment_event import (
    ProcessShipmentEventUsecase,
)
from order_service.infrastructure.http.notifications_client import (
    HttpNotificationsClient,
)
from order_service.infrastructure.kafka.consumer import (
    ShipmentEventsConsumer,
)
from order_service.infrastructure.kafka.outbox_dispatcher import (
    OutboxDispatcher,
)
from order_service.infrastructure.kafka.producer import KafkaEventPublisher
from order_service.infrastructure.notifications.dispatcher import (
    NotificationDispatcher,
)
from order_service.infrastructure.persistence.database import SessionFactory
from order_service.infrastructure.persistence.unit_of_work import (
    SqlAlchemyUnitOfWork,
)
from order_service.settings import settings

_event_publisher = KafkaEventPublisher(
    bootstrap_servers=settings.kafka.bootstrap_servers
)

_outbox_dispatcher = OutboxDispatcher(
    uow_factory=lambda: SqlAlchemyUnitOfWork(SessionFactory),
    publisher=_event_publisher,
    interval_seconds=settings.kafka.outbox_dispatch_interval_seconds,
    max_attempts=settings.kafka.outbox_attempts_max,
    batch_limit=settings.kafka.outbox_batch_limit,
)

_shipment_events_consumer = ShipmentEventsConsumer(
    bootstrap_servers=settings.kafka.bootstrap_servers,
    usecase_factory=lambda: ProcessShipmentEventUsecase(
        SqlAlchemyUnitOfWork(SessionFactory)
    ),
    group_id=settings.kafka.consumer_group_id,
)

_notifications_client = HttpNotificationsClient(
    base_url=settings.capashino.base_url,
    api_key=settings.capashino.api_secret_key,
)

_notification_dispatcher = NotificationDispatcher(
    uow_factory=lambda: SqlAlchemyUnitOfWork(SessionFactory),
    client=_notifications_client,
    interval_seconds=settings.notifications.outbox_dispatch_interval_seconds,
    max_attempts=settings.notifications.outbox_attempts_max,
    batch_limit=settings.notifications.outbox_batch_limit,
)


async def start_background_workers() -> None:
    await _event_publisher.start()
    _outbox_dispatcher.start()
    await _shipment_events_consumer.start()
    _notification_dispatcher.start()


async def stop_background_workers() -> None:
    await _notification_dispatcher.stop()
    await _notifications_client.aclose()
    await _shipment_events_consumer.stop()
    await _outbox_dispatcher.stop()
    await _event_publisher.stop()
