"""In-memory PIR repository."""

from __future__ import annotations

from datetime import datetime
from typing import Mapping, Sequence

from .criteria import Criterion
from .errors import PIRNotFoundError, ValidationError
from .pir import ContactPIR, EventPIR, PIR, PlainTextPIR, TaskPIR


class PIRRepository:
    """Owns PIR identifiers and records for one local session."""

    def __init__(self) -> None:
        self._records: dict[int, PIR] = {}
        self._next_id = 1

    def create_plain_text(self, content: str) -> PlainTextPIR:
        record = PlainTextPIR(self._next_id, content)
        self._add_new(record)
        return record

    def create_task(self, description: str, deadline: datetime | str) -> TaskPIR:
        record = TaskPIR(self._next_id, description, deadline)
        self._add_new(record)
        return record

    def create_event(
        self,
        description: str,
        start: datetime | str,
        alarm: datetime | str,
    ) -> EventPIR:
        record = EventPIR(self._next_id, description, start, alarm)
        self._add_new(record)
        return record

    def create_contact(self, name: str, address: str, mobile: str) -> ContactPIR:
        record = ContactPIR(self._next_id, name, address, mobile)
        self._add_new(record)
        return record

    def get(self, record_id: int) -> PIR:
        if record_id not in self._records:
            raise PIRNotFoundError(f"PIR {record_id} does not exist")
        return self._records[record_id]

    def update(self, record_id: int, changes: Mapping[str, object]) -> PIR:
        record = self.get(record_id)
        record.update(changes)
        return record

    def search(self, criterion: Criterion) -> list[PIR]:
        if not isinstance(criterion, Criterion):
            raise ValidationError("search requires a Criterion")
        return [record for record in self.all() if criterion.evaluate(record)]

    def all(self) -> list[PIR]:
        return [self._records[record_id] for record_id in sorted(self._records)]

    def delete(self, record_id: int) -> None:
        if record_id not in self._records:
            raise PIRNotFoundError(f"PIR {record_id} does not exist")
        del self._records[record_id]

    def replace(self, records: Sequence[PIR]) -> None:
        replacement: dict[int, PIR] = {}
        for record in records:
            if not isinstance(record, PIR):
                raise ValidationError("all replacement values must be PIR objects")
            if record.id in replacement:
                raise ValidationError(f"duplicate PIR id {record.id}")
            replacement[record.id] = record
        self._records = replacement
        self._next_id = max(replacement, default=0) + 1

    def _add_new(self, record: PIR) -> None:
        self._records[record.id] = record
        self._next_id += 1
