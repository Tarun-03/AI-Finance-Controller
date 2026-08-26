from enum import Enum

class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class TransactionType(str, Enum):
    PAYMENT = "PAYMENT"
    REFUND = "REFUND"


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class PaymentMethod(str, Enum):
    UPI = "UPI"
    CARD = "CARD"
    NET_BANKING = "NET_BANKING"
    WALLET = "WALLET"


class SettlementStatus(str, Enum):
    PENDING = "PENDING"
    SETTLED = "SETTLED"
    FAILED = "FAILED"


class ReconciliationStatus(str, Enum):
    PENDING = "PENDING"
    MATCHED = "MATCHED"
    MISMATCH = "MISMATCH"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"


class ExceptionStatus(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"
    REJECTED = "REJECTED"


class ExceptionSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class InvoiceStatus(str, Enum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"

class ExceptionType(str, Enum):
    AMOUNT_MISMATCH = "AMOUNT_MISMATCH"
    MISSING_PAYMENT = "MISSING_PAYMENT"
    MISSING_SETTLEMENT = "MISSING_SETTLEMENT"
    MISSING_INVOICE = "MISSING_INVOICE"
    FEE_MISMATCH = "FEE_MISMATCH"
    TAX_MISMATCH = "TAX_MISMATCH"
    STATUS_MISMATCH = "STATUS_MISMATCH"
    UNKNOWN = "UNKNOWN"