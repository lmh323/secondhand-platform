"""Values returned by controller operations."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..model.pir import PIR


@dataclass(frozen=True)
class OperationResult:
    """Presentation-neutral result sent from Controller to View."""

    status: str
    message: str = ""
    records: tuple[PIR, ...] = field(default_factory=tuple)
