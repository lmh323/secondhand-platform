"""Unit tests for the versioned .pim persistence format."""

from __future__ import annotations

import json
import unittest

from src.model.errors import PersistenceError, ValidationError
from src.model.persistence import PIRFactory, PIMSerializer
from src.model.pir import PlainTextPIR
from src.model.repository import PIRRepository
from tests.support import WorkspaceTestCase


class PersistenceTests(WorkspaceTestCase):
    def test_round_trip_preserves_all_record_types_and_ids(self) -> None:
        repository = PIRRepository()
        repository.create_plain_text("title: iPad Air")
        repository.create_task("Confirm payment", "2026-11-20 18:00")
        repository.create_event("Campus handover", "2026-11-21 14:00", "2026-11-21 13:30")
        repository.create_contact("Chan Tai Man", "Hung Hom", "91234567")
        path = self.artifact_path()

        PIMSerializer.save(repository.all(), path)
        restored = PIMSerializer.load(path)

        self.assertEqual(
            [record.to_dict() for record in restored],
            [record.to_dict() for record in repository.all()],
        )
        self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["schema_version"], 1)

    def test_save_validates_path_and_record_values(self) -> None:
        with self.assertRaises(PersistenceError):
            PIMSerializer.save([], self.artifact_path("data.json"))
        with self.assertRaises(ValidationError):
            PIMSerializer.save([object()], self.artifact_path())  # type: ignore[list-item]
        with self.assertRaises(PersistenceError):
            PIMSerializer.save(
                [PlainTextPIR(1, "one"), PlainTextPIR(1, "duplicate")], self.artifact_path("dup.pim")
            )

    def test_factory_rejects_missing_extra_and_unknown_record_fields(self) -> None:
        with self.assertRaises(ValidationError):
            PIRFactory.from_dict({"id": 1, "type": "text"})
        with self.assertRaises(ValidationError):
            PIRFactory.from_dict({"id": 1, "type": "text", "content": "x", "extra": "bad"})
        with self.assertRaises(ValidationError):
            PIRFactory.from_dict({"id": 1, "type": "unsupported", "value": "x"})

    def test_load_rejects_missing_malformed_incompatible_and_duplicate_files(self) -> None:
        missing = self.artifact_path("missing.pim")
        with self.assertRaises(PersistenceError):
            PIMSerializer.load(missing)

        cases = {
            "invalid-json.pim": "{",
            "wrong-top-level.pim": "[]",
            "wrong-schema.pim": json.dumps({"schema_version": 2, "records": []}),
            "wrong-records.pim": json.dumps({"schema_version": 1, "records": {}}),
            "duplicate-ids.pim": json.dumps(
                {
                    "schema_version": 1,
                    "records": [
                        {"id": 1, "type": "text", "content": "one"},
                        {"id": 1, "type": "text", "content": "two"},
                    ],
                }
            ),
        }
        for filename, content in cases.items():
            path = self.artifact_path(filename)
            path.write_text(content, encoding="utf-8")
            with self.subTest(filename=filename):
                with self.assertRaises(PersistenceError):
                    PIMSerializer.load(path)

