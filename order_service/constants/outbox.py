from enum import StrEnum


class OutboxStatus(StrEnum):
    pending = 'pending'
    sent = 'sent'
    failed = 'failed'
