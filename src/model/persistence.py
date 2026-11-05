"""Versioned .pim persistence."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Sequence

from .errors import PersistenceError, ValidationError
from .pir import ContactPIR, EventPIR, PIR, PlainTextPIR, TaskPIR
from .time_utils import parse_datetime

SCHEMA_VERSION = 1


class PIRFactory:
    """Reconstruct PIR instances from validated persistence dictionaries."""

    @staticmethod
    def from_dict(data: dict[str, Any]) -> PIR:
        if not isinstance(data, dict):
            raise ValidationError("each record must be an object")
        record_type = data.get("type")
        record_id = data.get("id")
        if record_type == "text":
            PIRFactory._require_keys(data, {"id", "type", "content"})
            return PlainTextPIR(record_id, data["content"])
        if record_type == "task":
            PIRFactory._require_keys(data, {"id", "type", "description", "deadline"})
            return TaskPIR(record_id, data["description"], parse_datetime(data["deadline"], field_name="deadline"))
        if record_type == "event":
            PIRFactory._require_keys(data, {"id", "type", "description", "start", "alarm"})
            return EventPIR(
                record_id,
                data["description"],
                parse_datetime(data["start"], field_name="start"),
                parse_datetime(data["alarm"], field_name="alarm"),
            )
        if record_type == "contact":
            PIRFactory._require_keys(data, {"id", "type", "name", "address", "mobile"})
            return ContactPIR(record_id, data["name"], data["address"], data["mobile"])
        raise ValidationError(f"unsupported PIR type '{record_type}'")

    @staticmethod
    def _require_keys(data: dict[str, Any], expected: set[str]) -> None:
        actual = set(data)
        if actual != expected:
            missing = sorted(expected - actual)
            extra = sorted(actual - expected)
            details: list[str] = []
            if missing:
                details.append(f"missing {', '.join(missing)}")
            if extra:
                details.append(f"unknown {', '.join(extra)}")
            raise ValidationError("invalid record fields: " + "; ".join(details))


class PIMSerializer:
    """Save and load the repository's stable JSON-based .pim format."""

    @staticmethod
    def save(records: Sequence[PIR], path: Path | str) -> None:
        target = PIMSerializer._validate_path(path)
        try:
            if any(not isinstance(record, PIR) for record in records):
                raise ValidationError("all records to save must be PIR objects")
            serialized_records = [record.to_dict() for record in records]
            ids = [record["id"] for record in serialized_records]
            if len(ids) != len(set(ids)):
                raise PersistenceError("cannot save duplicate PIR identifiers")
            document = {"schema_version": SCHEMA_VERSION, "records": serialized_records}
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary_name: str | None = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode="w",
                    encoding="utf-8",
                    dir=target.parent,
                    prefix=f".{target.name}.",
                    suffix=".tmp",
                    delete=False,
                ) as stream:
                    temporary_name = stream.name
                    json.dump(document, stream, ensure_ascii=False, indent=2, sort_keys=True)
                    stream.write("\n")
                    stream.flush()
                os.replace(temporary_name, target)
                temporary_name = None
            finally:
                if temporary_name is not None:
                    try:
                        os.remove(temporary_name)
                    except OSError:
                        pass
        except PersistenceError:
            raise
        except (OSError, TypeError, ValueError) as error:
            raise PersistenceError(f"could not save '{target}': {error}") from error

    @staticmethod
    def load(path: Path | str) -> list[PIR]:
        target = PIMSerializer._validate_path(path)
        try:
            with target.open("r", encoding="utf-8") as stream:
                document = json.load(stream)
            if not isinstance(document, dict):
                raise ValidationError("top-level .pim value must be an object")
            if document.get("schema_version") != SCHEMA_VERSION:
                raise ValidationError(f"unsupported schema version {document.get('schema_version')}")
            raw_records = document.get("records")
            if not isinstance(raw_records, list):
                raise ValidationError(".pim records must be a list")
            records = [PIRFactory.from_dict(item) for item in raw_records]
            ids = [record.id for record in records]
            if len(ids) != len(set(ids)):
                raise ValidationError(".pim contains duplicate PIR identifiers")
            return records
        except PersistenceError:
            raise
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError, ValidationError) as error:
            raise PersistenceError(f"could not load '{target}': {error}") from error

    @staticmethod
    def _validate_path(path: Path | str) -> Path:
        target = Path(path)
        if target.suffix.lower() != ".pim":
            raise PersistenceError("file path must end with .pim")
        return target
