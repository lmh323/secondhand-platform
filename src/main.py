"""Entry point for the command-line PIM."""

from __future__ import annotations

import sys
from typing import TextIO

from .cli.command_parser import CommandParser, CommandSyntaxError
from .cli.controller import Controller
from .cli.result import OperationResult
from .cli.view import View


def run(input_stream: TextIO | None = None, output_stream: TextIO | None = None) -> None:
    """Run the command loop with injectable streams for verification."""

    input_stream = input_stream or sys.stdin
    view = View(output_stream or sys.stdout)
    controller = Controller()

    while True:
        view.render_prompt()
        line = input_stream.readline()
        if line == "":
            break
        try:
            command = CommandParser.parse(line)
        except CommandSyntaxError as error:
            view.render(OperationResult("error", str(error)))
            continue
        result = controller.execute(command)
        view.render(result)
        if result.status == "exit":
            break


if __name__ == "__main__":
    run()
