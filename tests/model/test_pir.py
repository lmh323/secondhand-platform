"""Unit tests for PIR validation, updates, and formatting."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from src.model.errors import ValidationError
from src.model.pir import ContactPIR, EventPIR, PlainTextPIR, TaskPIR


class PIRConstructionTests(unittest.TestCase):
    def test_all_record_types_store_required_fields(self) -> None:
        records = [
            PlainTextPIR(1, "title: iPad Air"),
            TaskPIR(2, "Confirm payment", "2026-11-20 18:00"),
            EventPIR(3, "Campus handover", "2026-11-21 14:00", "2026-11-21 13:30"),
            ContactPIR(4, "Chan Tai Man", "Hung Hom", "91234567"),
        ]

        self.assertEqual([record.id for record in records], [1, 2, 3, 4])
        self.assertEqual(
            [record.type_name for record in records], ["text", "task", "event", "contact"]
        )
        self.assertEqual(records[0].content, "title: iPad Air")
        self.assertEqual(records[1].deadline, datetime(2026, 11, 20, 18, 0))
        self.assertEqual(records[2].start, datetime(2026, 11, 21, 14, 0))
        self.assertEqual(records[3].mobile, "91234567")

    def test_serialization_and_display_preserve_values(self) -> None:
        task = TaskPIR(7, "Confirm payment", "2026-11-20 18:00")

        self.assertEqual(
            task.to_dict(),
            {
                "id": 7,
                "type": "task",
                "description": "Confirm payment",
                "deadline": "2026-11-20T18:00",
            },
        )
        self.assertIn("Deadline: 2026-11-20 18:00", task.format_details())

    def test_required_values_and_identifiers_are_validated(self) -> None:
        invalid_constructors = [
            lambda: PlainTextPIR(1, "   "),
            lambda: TaskPIR(1, "   ", "2026-11-20 18:00"),
            lambda: EventPIR(1, "handover", "bad", "2026-11-21 13:30"),
            lambda: ContactPIR(1, "buyer", "   ", "91234567"),
        ]
        for constructor in invalid_constructors:
            with self.subTest(constructor=constructor):
                with self.assertRaises(ValidationError):
                    constructor()

        for record_id in (0, -1, True, "1"):
            with self.subTest(record_id=record_id):
                with self.assertRaises(ValidationError):
                    PlainTextPIR(record_id, "content")

    def test_timezone_aware_datetimes_are_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            TaskPIR(1, "task", datetime(2026, 11, 20, 18, 0, tzinfo=timezone.utc))


class PIRUpdateTests(unittest.TestCase):
    def test_updates_change_fields_without_changing_identity_or_type(self) -> None:
        text = PlainTextPIR(1, "old listing")
        task = TaskPIR(2, "old task", "2026-11-20 18:00")
        event = EventPIR(3, "old event", "2026-11-21 14:00", "2026-11-21 13:30")
        contact = ContactPIR(4, "Old Name", "Old Address", "90000000")

        text.update({"content": "new listing"})
        task.update({"description": "new task", "deadline": "2026-11-22 09:00"})
        event.update(
            {
                "description": "new event",
                "start": "2026-11-23 10:00",
                "alarm": "2026-11-23 09:30",
            }
        )
        contact.update({"name": "New Name", "address": "New Address", "mobile": "91111111"})

        self.assertEqual((text.id, text.type_name, text.content), (1, "text", "new listing"))
        self.assertEqual((task.id, task.type_name, task.description), (2, "task", "new task"))
        self.assertEqual((event.id, event.type_name, event.description), (3, "event", "new event"))
        self.assertEqual((contact.id, contact.type_name, contact.name), (4, "contact", "New Name"))

    def test_invalid_multi_field_update_is_atomic(self) -> None:
        task = TaskPIR(1, "old task", "2026-11-20 18:00")
        with self.assertRaises(ValidationError):
            task.update({"description": "new task", "deadline": "invalid"})
        self.assertEqual(task.description, "old task")
        self.assertEqual(task.deadline, datetime(2026, 11, 20, 18, 0))

        contact = ContactPIR(2, "Name", "Address", "90000000")
        with self.assertRaises(ValidationError):
            contact.update({"name": "New Name", "mobile": ""})
        self.assertEqual(contact.name, "Name")
        self.assertEqual(contact.mobile, "90000000")

    def test_unknown_fields_are_rejected_but_known_missing_fields_do_not_match(self) -> None:
        text = PlainTextPIR(1, "listing")
        with self.assertRaises(ValidationError):
            text.update({"status": "sold"})
        with self.assertRaises(ValidationError):
            text.get_field("status")
        self.assertIsNone(text.get_field("deadline"))
