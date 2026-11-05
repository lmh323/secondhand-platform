"""Parse one command-line instruction into a typed command."""

from __future__ import annotations

import shlex
from dataclasses import dataclass, field


class CommandSyntaxError(Exception):
    """Raised when a command line cannot be tokenized or shaped."""


@dataclass(frozen=True)
class Command:
    """Parsed command data consumed by the controller."""

    name: str
    positionals: tuple[str, ...] = ()
    options: dict[str, str] = field(default_factory=dict)
    argument_text: str = ""


class CommandParser:
    """Convert the Stage 1 command syntax into Command objects."""

    _COMMANDS = frozenset(
        {"create", "update", "search", "print", "delete", "save", "load", "help", "exit"}
    )

    @classmethod
    def parse(cls, line: str) -> Command:
        if not isinstance(line, str):
            raise CommandSyntaxError("command must be text")
        stripped = line.strip()
        if not stripped:
            raise CommandSyntaxError("command cannot be empty")
        try:
            tokens = shlex.split(stripped, posix=True)
        except ValueError as error:
            raise CommandSyntaxError(f"invalid quoting: {error}") from error
        if not tokens:
            raise CommandSyntaxError("command cannot be empty")

        name = tokens[0].lower()
        if name not in cls._COMMANDS:
            raise CommandSyntaxError(f"unknown command '{tokens[0]}'")

        if name == "search":
            argument_text = stripped[len(tokens[0]) :].strip()
            return Command(name=name, argument_text=argument_text)

        if name == "create":
            if len(tokens) < 2:
                raise CommandSyntaxError("create requires a PIR type")
            return Command(
                name=name,
                positionals=(tokens[1].lower(),),
                options=cls._parse_options(tokens[2:]),
            )

        if name == "update":
            if len(tokens) < 2:
                raise CommandSyntaxError("update requires a PIR identifier")
            return Command(
                name=name,
                positionals=(tokens[1],),
                options=cls._parse_options(tokens[2:]),
            )

        return Command(name=name, positionals=tuple(tokens[1:]))

    @staticmethod
    def _parse_options(tokens: list[str]) -> dict[str, str]:
        options: dict[str, str] = {}
        for token in tokens:
            if "=" not in token:
                raise CommandSyntaxError(f"option '{token}' must use key=value")
            key, value = token.split("=", 1)
            key = key.strip().lower()
            if not key:
                raise CommandSyntaxError("option name cannot be empty")
            if key in options:
                raise CommandSyntaxError(f"option '{key}' was supplied more than once")
            options[key] = value
        return options
