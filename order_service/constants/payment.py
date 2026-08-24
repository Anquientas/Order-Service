from enum import StrEnum


class PaymentStatus(StrEnum):
    succeeded = 'succeeded'
    failed = 'failed'
