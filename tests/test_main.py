"""End-to-end command-loop verification."""

from __future__ import annotations

import io
import unittest

from src.main import run


class MainLoopTests(unittest.TestCase):
    def test_run_processes_commands_and_continues_after_syntax_errors(self) -> None:
        input_stream = io.StringIO(
            'create text content="title: iPad Air"\n'
            "bad-command\n"
            'search content contains "ipad"\n'
            "print all\n"
            "exit\n"
        )
        output_stream = io.StringIO()

        run(input_stream, output_stream)

        output = output_stream.getvalue()
        self.assertIn("OK: created PIR 1", output)
        self.assertIn("ERROR: unknown command 'bad-command'", output)
        self.assertIn("MATCHES: 1 record(s) matched", output)
        self.assertIn("Content: title: iPad Air", output)

    def test_run_stops_cleanly_at_end_of_input(self) -> None:
        output_stream = io.StringIO()
        run(io.StringIO("help\n"), output_stream)
        self.assertIn("Commands:", output_stream.getvalue())
