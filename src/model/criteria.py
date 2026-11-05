"""Search criterion tree and parser."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from .errors import CriterionParseError, ValidationError
from .pir import PIR
from .time_utils import parse_datetime

TYPE_NAMES = frozenset({"text", "task", "event", "contact"})
TEXT_FIELDS = frozenset({"content", "description", "name", "address", "mobile"})
TIME_FIELDS = frozenset({"deadline", "start", "alarm"})


class Criterion(ABC):
    """Boolean expression evaluated against one PIR."""

    @abstractmethod
    def evaluate(self, record: PIR) -> bool:
        """Return whether the record satisfies this criterion."""


@dataclass(frozen=True)
class PredicateCriterion(Criterion):
    field: str
    operator: str
    value: object

    def __post_init__(self) -> None:
        if self.field == "type":
            if self.operator != "=" or self.value not in TYPE_NAMES:
                raise ValidationError("type predicates require '= text|task|event|contact'")
        elif self.field in TEXT_FIELDS:
            if self.operator != "contains" or not isinstance(self.value, str):
                raise ValidationError("text predicates require 'contains' and a string")
        elif self.field in TIME_FIELDS:
            if self.operator not in {"<", ">", "="} or not isinstance(self.value, datetime):
                raise ValidationError("time predicates require <, >, or = and a datetime")
        else:
            raise ValidationError(f"unknown search field '{self.field}'")

    def evaluate(self, record: PIR) -> bool:
        if self.field == "type":
            return record.type_name == self.value

        value = record.get_field(self.field)
        if value is None:
            return False
        if self.field in TEXT_FIELDS:
            if not isinstance(value, str):
                return False
            return str(self.value).casefold() in value.casefold()

        if not isinstance(value, datetime):
            return False
        target = self.value
        if self.operator == "<":
            return value < target
        if self.operator == ">":
            return value > target
        return value == target


@dataclass(frozen=True)
class NotCriterion(Criterion):
    operand: Criterion

    def evaluate(self, record: PIR) -> bool:
        return not self.operand.evaluate(record)


@dataclass(frozen=True)
class AndCriterion(Criterion):
    left: Criterion
    right: Criterion

    def evaluate(self, record: PIR) -> bool:
        return self.left.evaluate(record) and self.right.evaluate(record)


@dataclass(frozen=True)
class OrCriterion(Criterion):
    left: Criterion
    right: Criterion

    def evaluate(self, record: PIR) -> bool:
        return self.left.evaluate(record) or self.right.evaluate(record)


@dataclass(frozen=True)
class _Token:
    value: str
    position: int


class CriterionParser:
    """Parse the Stage 1 criterion grammar into a criterion tree."""

    def __init__(self) -> None:
        self._tokens: list[_Token] = []
        self._index = 0

    def parse(self, expression: str) -> Criterion:
        if not isinstance(expression, str) or not expression.strip():
            raise CriterionParseError("criterion cannot be empty")
        self._tokens = self._tokenize(expression)
        self._index = 0
        criterion = self._parse_disjunction()
        if self._peek() is not None:
            token = self._peek()
            raise CriterionParseError(f"unexpected token '{token.value}' at position {token.position}")
        return criterion

    def _parse_disjunction(self) -> Criterion:
        left = self._parse_conjunction()
        while self._match("||"):
            left = OrCriterion(left, self._parse_conjunction())
        return left

    def _parse_conjunction(self) -> Criterion:
        left = self._parse_negation()
        while self._match("&&"):
            left = AndCriterion(left, self._parse_negation())
        return left

    def _parse_negation(self) -> Criterion:
        if self._match("!"):
            return NotCriterion(self._parse_negation())
        return self._parse_primary()

    def _parse_primary(self) -> Criterion:
        if self._match("("):
            criterion = self._parse_disjunction()
            self._expect(")")
            return criterion
        return self._parse_predicate()

    def _parse_predicate(self) -> Criterion:
        field = self._consume("field").value
        if field == "type":
            self._expect("=")
            type_name = self._consume("type name").value
            try:
                return PredicateCriterion(field, "=", type_name)
            except ValidationError as error:
                raise CriterionParseError(str(error)) from error
        if field in TEXT_FIELDS:
            self._expect("contains")
            text = self._consume("quoted text").value
            try:
                return PredicateCriterion(field, "contains", text)
            except ValidationError as error:
                raise CriterionParseError(str(error)) from error
        if field in TIME_FIELDS:
            operator = self._consume("time operator").value
            if operator not in {"<", ">", "="}:
                raise CriterionParseError(f"invalid time operator '{operator}'")
            value = self._consume("quoted time").value
            try:
                parsed = parse_datetime(value, field_name=field)
                return PredicateCriterion(field, operator, parsed)
            except ValidationError as error:
                raise CriterionParseError(str(error)) from error
        raise CriterionParseError(f"unknown search field '{field}'")

    def _tokenize(self, expression: str) -> list[_Token]:
        tokens: list[_Token] = []
        i = 0
        length = len(expression)
        while i < length:
            char = expression[i]
            if char.isspace():
                i += 1
                continue
            if char in "()=!<>":
                tokens.append(_Token(char, i))
                i += 1
                continue
            if char in "&|":
                if i + 1 >= length or expression[i + 1] != char:
                    raise CriterionParseError(f"operator '{char}' must be doubled at position {i}")
                tokens.append(_Token(char * 2, i))
                i += 2
                continue
            if char == '"':
                start = i
                i += 1
                value: list[str] = []
                while i < length:
                    if expression[i] == '\\':
                        if i + 1 >= length:
                            raise CriterionParseError(f"unfinished escape at position {i}")
                        value.append(expression[i + 1])
                        i += 2
                        continue
                    if expression[i] == '"':
                        i += 1
                        break
                    value.append(expression[i])
                    i += 1
                else:
                    raise CriterionParseError(f"unterminated quoted value at position {start}")
                tokens.append(_Token("".join(value), start))
                continue

            start = i
            while i < length and not expression[i].isspace() and expression[i] not in "()=!<>&|\"":
                i += 1
            if start == i:
                raise CriterionParseError(f"unexpected character '{expression[i]}' at position {i}")
            tokens.append(_Token(expression[start:i], start))
        return tokens

    def _peek(self) -> _Token | None:
        if self._index >= len(self._tokens):
            return None
        return self._tokens[self._index]

    def _match(self, value: str) -> bool:
        token = self._peek()
        if token is not None and token.value == value:
            self._index += 1
            return True
        return False

    def _expect(self, value: str) -> _Token:
        token = self._peek()
        if token is None or token.value != value:
            actual = "end of expression" if token is None else f"'{token.value}'"
            raise CriterionParseError(f"expected '{value}', found {actual}")
        self._index += 1
        return token

    def _consume(self, description: str) -> _Token:
        token = self._peek()
        if token is None:
            raise CriterionParseError(f"expected {description}, found end of expression")
        self._index += 1
        return token
