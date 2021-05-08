from enum import Enum


class TransactionState(Enum):
    PENDING = "pending"
    COMPLETE = "complete"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REVERTED = "reverted"
