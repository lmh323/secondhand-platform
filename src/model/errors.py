"""Stable exception types exposed by the model layer."""


class PIMError(Exception):
    """Base class for expected PIM failures."""


class ValidationError(PIMError):
    """Raised when a value or model operation violates a requirement."""


class PIRNotFoundError(PIMError):
    """Raised when a requested PIR identifier is not in the repository."""


class CriterionParseError(PIMError):
    """Raised when a search criterion cannot be parsed."""


class PersistenceError(PIMError):
    """Raised when a .pim file cannot be saved or loaded safely."""
