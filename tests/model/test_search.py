"""Unit tests for criterion parsing and evaluation."""

from __future__ import annotations

import unittest

from src.model.criteria import CriterionParser, PredicateCriterion
from src.model.errors import CriterionParseError, ValidationError
from src.model.repository import PIRRepository


class SearchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = PIRRepository()
        self.repository.create_plain_text(
            "title: iPad Air; category: electronics; status: available"
        )
        self.repository.create_task("Confirm payment", "2026-11-20 18:00")
        self.repository.create_task("Read buyer message", "2026-11-30 09:00")
        self.repository.create_event(
            "Campus handover", "2026-11-21 14:00", "2026-11-21 13:30"
        )
        self.repository.create_contact("Chan Tai Man", "Hung Hom", "91234567")
        self.parser = CriterionParser()

    def test_type_and_case_insensitive_text_search(self) -> None:
        criterion = self.parser.parse('type = text && content contains "IPAD"')
        records = self.repository.search(criterion)
        self.assertEqual([record.id for record in records], [1])

    def test_time_search_skips_records_without_the_requested_field(self) -> None:
        deadline = self.parser.parse('deadline < "2026-11-25 00:00"')
        start = self.parser.parse('start > "2026-11-20 00:00"')

        self.assertEqual([record.id for record in self.repository.search(deadline)], [2])
        self.assertEqual([record.id for record in self.repository.search(start)], [4])

    def test_boolean_precedence_and_parentheses(self) -> None:
        precedence = self.parser.parse(
            'type = text || type = task && description contains "payment"'
        )
        grouped = self.parser.parse(
            'type = task && (description contains "payment" || description contains "buyer")'
        )
        negated = self.parser.parse("!(type = contact)")

        self.assertEqual([record.id for record in self.repository.search(precedence)], [1, 2])
        self.assertEqual([record.id for record in self.repository.search(grouped)], [2, 3])
        self.assertEqual([record.id for record in self.repository.search(negated)], [1, 2, 3, 4])

    def test_time_equality_and_all_text_fields_are_supported(self) -> None:
        self.assertEqual(
            [record.id for record in self.repository.search(self.parser.parse('alarm = "2026-11-21 13:30"'))],
            [4],
        )
        self.assertEqual(
            [record.id for record in self.repository.search(self.parser.parse('name contains "CHAN"'))],
            [5],
        )
        self.assertEqual(
            [record.id for record in self.repository.search(self.parser.parse('address contains "hung"'))],
            [5],
        )
        self.assertEqual(
            [record.id for record in self.repository.search(self.parser.parse('mobile contains "123"'))],
            [5],
        )

    def test_invalid_criteria_are_rejected(self) -> None:
        invalid_expressions = (
            "",
            "type = unknown",
            'description = "payment"',
            'deadline != "2026-11-20 18:00"',
            "type = text &&",
            "(type = text",
            "type = text & type = task",
            'type = text ||| type = task',
        )
        for expression in invalid_expressions:
            with self.subTest(expression=expression):
                with self.assertRaises(CriterionParseError):
                    self.parser.parse(expression)

    def test_predicate_constructor_rejects_invalid_field_definitions(self) -> None:
        with self.assertRaises(ValidationError):
            PredicateCriterion("unknown", "=", "value")
        with self.assertRaises(ValidationError):
            PredicateCriterion("type", "contains", "text")
        with self.assertRaises(ValidationError):
            PredicateCriterion("content", "=", "text")
