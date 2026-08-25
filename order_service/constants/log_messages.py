from enum import StrEnum


class OutboxDispatcherLogMessage(StrEnum):
    dispatch_cycle_failed = 'Outbox dispatch cycle failed'
    permanently_failed = (
        'Outbox record %s permanently failed after %s attempts: %s'
    )
    retry_attempt_failed = 'Outbox record %s publish attempt %s failed: %s'


class ShipmentConsumerLogMessage(StrEnum):
    processing_failed = 'Failed to process shipment event at %s:%s:%s'


class NotificationDispatcherLogMessage(StrEnum):
    dispatch_cycle_failed = 'Notification dispatch cycle failed'
    permanently_failed = (
        'Notification %s permanently failed after %s attempts: %s'
    )
    retry_attempt_failed = 'Notification %s send attempt %s failed: %s'
