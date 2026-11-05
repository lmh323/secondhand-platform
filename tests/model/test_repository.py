"""Unit tests for repository lifecycle operations."""

from __future__ import annotations

import unittest

from src.model.criteria import CriterionParser
from src.model.errors import PIRNotFoundError, ValidationError
from src.model.pir import PlainTextPIR
from src.model.repository import PIRRepository


class RepositoryTests(unittest.TestCase):
    def test_create_assigns_sequential_ids_and_invalid_create_does_not_consume_one(self) -> None:
        repository = PIRRepository()
        with self.assertRaises(ValidationError):
            repository.create_task("", "2026-11-20 18:00")
        first = repository.create_plain_text("first")
        second = repository.create_contact("Name", "Address", "90000000")

        self.assertEqual((first.id, second.id), (1, 2))
        self.assertEqual([record.id for record in repository.all()], [1, 2])

    def test_get_update_delete_and_missing_ids(self) -> None:
        repository = PIRRepository()
        record = repository.create_plain_text("old")
        repository.update(record.id, {"content": "new"})
        self.assertEqual(repository.get(record.id).content, "new")

        repository.delete(record.id)
        self.assertEqual(repository.all(), [])
        with self.assertRaises(PIRNotFoundError):
            repository.get(record.id)
        with self.assertRaises(PIRNotFoundError):
            repository.delete(record.id)

    def test_search_requires_a_criterion(self) -> None:
        repository = PIRRepository()
        repository.create_plain_text("listing")
        criterion = CriterionParser().parse('content contains "listing"')
        self.assertEqual([record.id for record in repository.search(criterion)], [1])
        with self.assertRaises(ValidationError):
            repository.search(object())  # type: ignore[arg-type]

    def test_replace_sorts_records_and_resets_next_identifier(self) -> None:
        repository = PIRRepository()
        repository.replace([PlainTextPIR(10, "ten"), PlainTextPIR(3, "three")])
        self.assertEqual([record.id for record in repository.all()], [3, 10])
        created = repository.create_plain_text("next")
        self.assertEqual(created.id, 11)

    def test_invalid_replace_is_atomic(self) -> None:
        repository = PIRRepository()
        original = repository.create_plain_text("original")
        with self.assertRaises(ValidationError):
            repository.replace([PlainTextPIR(2, "new"), PlainTextPIR(2, "duplicate")])
        self.assertEqual([record.to_dict() for record in repository.all()], [original.to_dict()])
