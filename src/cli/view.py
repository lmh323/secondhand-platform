"""Terminal rendering for controller results."""

from __future__ import annotations

import sys
from typing import TextIO

from .result import OperationResult


class View:
    """Render prompts, results, and errors for a command-line user."""

    def __init__(self, output: TextIO | None = None) -> None:
        self.output = output or sys.stdout

    def render_prompt(self) -> None:
        self.output.write("pim> ")
        self.output.flush()

    def render(self, result: OperationResult) -> None:
        if result.status == "exit":
            return
        if result.status == "help":
            self.output.write(result.message.rstrip() + "\n")
            return
        if result.status == "error":
            self.output.write(f"ERROR: {result.message}\n")
            return
        if result.status == "matches":
            self.output.write(f"MATCHES: {result.message}\n")
            self._render_records(result)
            return
        self.output.write(f"OK: {result.message}\n")
        self._render_records(result)

    def _render_records(self, result: OperationResult) -> None:
        for index, record in enumerate(result.records):
            if index:
                self.output.write("\n")
            self.output.write(record.format_details() + "\n")
