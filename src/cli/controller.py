"""Application controller for command-line use cases."""

from __future__ import annotations

from pathlib import Path

from ..model.criteria import CriterionParser
from ..model.errors import PIMError
from ..model.persistence import PIMSerializer
from ..model.repository import PIRRepository
from .command_parser import Command
from .result import OperationResult


HELP_TEXT = """Commands:
  create text content=\"...\"
  create task description=\"...\" deadline=\"YYYY-MM-DD HH:MM\"
  create event description=\"...\" start=\"YYYY-MM-DD HH:MM\" alarm=\"YYYY-MM-DD HH:MM\"
  create contact name=\"...\" address=\"...\" mobile=\"...\"
  update <id> field=\"value\" [field=\"value\" ...]
  search <criterion>
  print <id>
  print all
  delete <id>
  save <file.pim>
  load <file.pim>
  help
  exit

Text values containing spaces must be enclosed in double quotes.
Search supports type = ..., contains, <, >, =, !, &&, ||, and parentheses.
"""


class Controller:
    """Coordinate parsed commands and model operations."""

    def __init__(self, repository: PIRRepository | None = None) -> None:
        self.repository = repository or PIRRepository()
        self.criterion_parser = CriterionParser()

    def execute(self, command: Command) -> OperationResult:
        try:
            if command.name == "create":
                return self._create(command)
            if command.name == "update":
                return self._update(command)
            if command.name == "search":
                return self._search(command)
            if command.name == "print":
                return self._print(command)
            if command.name == "delete":
                return self._delete(command)
            if command.name == "save":
                return self._save(command)
            if command.name == "load":
                return self._load(command)
            if command.name == "help":
                return self._help(command)
            if command.name == "exit":
                return self._exit(command)
            return OperationResult("error", f"unknown command '{command.name}'")
        except PIMError as error:
            return OperationResult("error", str(error))
        except (TypeError, ValueError) as error:
            return OperationResult("error", str(error))

    def _create(self, command: Command) -> OperationResult:
        self._require_positionals(command, 1, "create")
        record_type = command.positionals[0]
        options = command.options
        if record_type == "text":
            self._require_options(options, {"content"})
            record = self.repository.create_plain_text(options["content"])
        elif record_type == "task":
            self._require_options(options, {"description", "deadline"})
            record = self.repository.create_task(options["description"], options["deadline"])
        elif record_type == "event":
            self._require_options(options, {"description", "start", "alarm"})
            record = self.repository.create_event(
                options["description"], options["start"], options["alarm"]
            )
        elif record_type == "contact":
            self._require_options(options, {"name", "address", "mobile"})
            record = self.repository.create_contact(
                options["name"], options["address"], options["mobile"]
            )
        else:
            raise ValueError(f"unsupported PIR type '{record_type}'")
        return OperationResult("ok", f"created PIR {record.id}", (record,))

    def _update(self, command: Command) -> OperationResult:
        self._require_positionals(command, 1, "update")
        if not command.options:
            raise ValueError("update requires at least one field=value option")
        record_id = self._parse_id(command.positionals[0])
        record = self.repository.update(record_id, command.options)
        return OperationResult("ok", f"updated PIR {record.id}", (record,))

    def _search(self, command: Command) -> OperationResult:
        criterion = self.criterion_parser.parse(command.argument_text)
        records = tuple(self.repository.search(criterion))
        return OperationResult("matches", f"{len(records)} record(s) matched", records)

    def _print(self, command: Command) -> OperationResult:
        self._require_positionals(command, 1, "print")
        if len(command.positionals) != 1:
            raise ValueError("print accepts one identifier or 'all'")
        target = command.positionals[0].lower()
        records = tuple(self.repository.all()) if target == "all" else (self.repository.get(self._parse_id(target)),)
        return OperationResult("ok", f"{len(records)} record(s)", records)

    def _delete(self, command: Command) -> OperationResult:
        self._require_positionals(command, 1, "delete")
        if len(command.positionals) != 1:
            raise ValueError("delete accepts one identifier")
        record_id = self._parse_id(command.positionals[0])
        self.repository.delete(record_id)
        return OperationResult("ok", f"deleted PIR {record_id}")

    def _save(self, command: Command) -> OperationResult:
        self._require_positionals(command, 1, "save")
        if len(command.positionals) != 1:
            raise ValueError("save accepts one .pim path")
        path = Path(command.positionals[0])
        PIMSerializer.save(self.repository.all(), path)
        return OperationResult("ok", f"saved {len(self.repository.all())} record(s) to {path}")

    def _load(self, command: Command) -> OperationResult:
        self._require_positionals(command, 1, "load")
        if len(command.positionals) != 1:
            raise ValueError("load accepts one .pim path")
        path = Path(command.positionals[0])
        records = PIMSerializer.load(path)
        self.repository.replace(records)
        return OperationResult("ok", f"loaded {len(records)} record(s) from {path}")

    @staticmethod
    def _help(command: Command) -> OperationResult:
        if command.positionals or command.options:
            raise ValueError("help does not accept arguments")
        return OperationResult("help", HELP_TEXT)

    @staticmethod
    def _exit(command: Command) -> OperationResult:
        if command.positionals or command.options:
            raise ValueError("exit does not accept arguments")
        return OperationResult("exit")

    @staticmethod
    def _require_positionals(command: Command, minimum: int, name: str) -> None:
        if len(command.positionals) < minimum:
            raise ValueError(f"{name} requires more arguments")

    @staticmethod
    def _require_options(options: dict[str, str], expected: set[str]) -> None:
        actual = set(options)
        missing = expected - actual
        extra = actual - expected
        if missing or extra:
            details: list[str] = []
            if missing:
                details.append(f"missing {', '.join(sorted(missing))}")
            if extra:
                details.append(f"unknown {', '.join(sorted(extra))}")
            raise ValueError("invalid options: " + "; ".join(details))

    @staticmethod
    def _parse_id(value: str) -> int:
        try:
            record_id = int(value)
        except ValueError as error:
            raise ValueError("PIR identifier must be a positive integer") from error
        if record_id <= 0:
            raise ValueError("PIR identifier must be a positive integer")
        return record_id
