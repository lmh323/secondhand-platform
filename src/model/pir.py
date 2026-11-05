"""PIR entities for the second-hand PIM."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, ClassVar, Mapping

from .errors import ValidationError
from .time_utils import format_file_datetime, parse_datetime


def _required_text(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be text")
    cleaned = value.strip()
    if not cleaned:
        raise ValidationError(f"{field_name} cannot be empty")
    return cleaned


def _required_id(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValidationError("id must be a positive integer")
    return value


class PIR(ABC):
    """Common interface implemented by every Personal Information Record."""

    type_name: ClassVar[str]
    _KNOWN_FIELD_NAMES: ClassVar[frozenset[str]] = frozenset(
        {
            "content",
            "description",
            "name",
            "address",
            "mobile",
            "deadline",
            "start",
            "alarm",
        }
    )

    def __init__(self, record_id: int) -> None:
        self.id = _required_id(record_id)

    @abstractmethod
    def allowed_fields(self) -> frozenset[str]:
        """Return field names that can be searched or updated."""

    def get_field(self, name: str) -> object | None:
        """Return a field value, or None when the field does not apply."""

        values = self._field_values()
        if name in values:
            return values[name]
        if name in self._KNOWN_FIELD_NAMES:
            return None
        raise ValidationError(f"unknown field '{name}' for {self.type_name}")

    @abstractmethod
    def _field_values(self) -> dict[str, object]:
        """Return the concrete fields used by search and display."""

    @abstractmethod
    def update(self, changes: Mapping[str, object]) -> None:
        """Apply a validated, atomic set of field changes."""

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Return the serializable representation of this record."""

    @abstractmethod
    def format_details(self) -> str:
        """Return stable human-readable output for the CLI view."""

    def _validate_update_fields(self, changes: Mapping[str, object]) -> None:
        if not isinstance(changes, Mapping) or not changes:
            raise ValidationError("at least one update field is required")
        unknown = set(changes) - self.allowed_fields()
        if unknown:
            names = ", ".join(sorted(str(name) for name in unknown))
            raise ValidationError(f"unknown field(s) for {self.type_name}: {names}")


class PlainTextPIR(PIR):
    """Free-form text used for a listing or note."""

    type_name = "text"

    def __init__(self, record_id: int, content: str) -> None:
        super().__init__(record_id)
        self.content = _required_text(content, "content")

    def allowed_fields(self) -> frozenset[str]:
        return frozenset({"content"})

    def _field_values(self) -> dict[str, object]:
        return {"content": self.content}

    def update(self, changes: Mapping[str, object]) -> None:
        self._validate_update_fields(changes)
        content = _required_text(changes["content"], "content")
        self.content = content

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "type": self.type_name, "content": self.content}

    def format_details(self) -> str:
        return f"ID: {self.id}\nType: Plain Text\nContent: {self.content}"


class TaskPIR(PIR):
    """Action with a description and deadline."""

    type_name = "task"

    def __init__(self, record_id: int, description: str, deadline: datetime | str) -> None:
        super().__init__(record_id)
        self.description = _required_text(description, "description")
        self.deadline = parse_datetime(deadline, field_name="deadline")

    def allowed_fields(self) -> frozenset[str]:
        return frozenset({"description", "deadline"})

    def _field_values(self) -> dict[str, object]:
        return {"description": self.description, "deadline": self.deadline}

    def update(self, changes: Mapping[str, object]) -> None:
        self._validate_update_fields(changes)
        new_description = self.description
        new_deadline = self.deadline
        if "description" in changes:
            new_description = _required_text(changes["description"], "description")
        if "deadline" in changes:
            new_deadline = parse_datetime(changes["deadline"], field_name="deadline")  # type: ignore[arg-type]
        self.description = new_description
        self.deadline = new_deadline

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type_name,
            "description": self.description,
            "deadline": format_file_datetime(self.deadline),
        }

    def format_details(self) -> str:
        return (
            f"ID: {self.id}\nType: Task\nDescription: {self.description}\n"
            f"Deadline: {self.deadline.strftime('%Y-%m-%d %H:%M')}"
        )


class EventPIR(PIR):
    """Scheduled event with a starting time and alarm."""

    type_name = "event"

    def __init__(
        self,
        record_id: int,
        description: str,
        start: datetime | str,
        alarm: datetime | str,
    ) -> None:
        super().__init__(record_id)
        self.description = _required_text(description, "description")
        self.start = parse_datetime(start, field_name="start")
        self.alarm = parse_datetime(alarm, field_name="alarm")

    def allowed_fields(self) -> frozenset[str]:
        return frozenset({"description", "start", "alarm"})

    def _field_values(self) -> dict[str, object]:
        return {"description": self.description, "start": self.start, "alarm": self.alarm}

    def update(self, changes: Mapping[str, object]) -> None:
        self._validate_update_fields(changes)
        new_description = self.description
        new_start = self.start
        new_alarm = self.alarm
        if "description" in changes:
            new_description = _required_text(changes["description"], "description")
        if "start" in changes:
            new_start = parse_datetime(changes["start"], field_name="start")  # type: ignore[arg-type]
        if "alarm" in changes:
            new_alarm = parse_datetime(changes["alarm"], field_name="alarm")  # type: ignore[arg-type]
        self.description = new_description
        self.start = new_start
        self.alarm = new_alarm

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type_name,
            "description": self.description,
            "start": format_file_datetime(self.start),
            "alarm": format_file_datetime(self.alarm),
        }

    def format_details(self) -> str:
        return (
            f"ID: {self.id}\nType: Event\nDescription: {self.description}\n"
            f"Start: {self.start.strftime('%Y-%m-%d %H:%M')}\n"
            f"Alarm: {self.alarm.strftime('%Y-%m-%d %H:%M')}"
        )


class ContactPIR(PIR):
    """Buyer or seller contact information."""

    type_name = "contact"

    def __init__(self, record_id: int, name: str, address: str, mobile: str) -> None:
        super().__init__(record_id)
        self.name = _required_text(name, "name")
        self.address = _required_text(address, "address")
        self.mobile = _required_text(mobile, "mobile")

    def allowed_fields(self) -> frozenset[str]:
        return frozenset({"name", "address", "mobile"})

    def _field_values(self) -> dict[str, object]:
        return {"name": self.name, "address": self.address, "mobile": self.mobile}

    def update(self, changes: Mapping[str, object]) -> None:
        self._validate_update_fields(changes)
        new_name = self.name
        new_address = self.address
        new_mobile = self.mobile
        if "name" in changes:
            new_name = _required_text(changes["name"], "name")
        if "address" in changes:
            new_address = _required_text(changes["address"], "address")
        if "mobile" in changes:
            new_mobile = _required_text(changes["mobile"], "mobile")
        self.name = new_name
        self.address = new_address
        self.mobile = new_mobile

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type_name,
            "name": self.name,
            "address": self.address,
            "mobile": self.mobile,
        }

    def format_details(self) -> str:
        return (
            f"ID: {self.id}\nType: Contact\nName: {self.name}\n"
            f"Address: {self.address}\nMobile: {self.mobile}"
        )
