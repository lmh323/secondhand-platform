"""CLI parser, controller, and view verification."""

from __future__ import annotations

import io
import unittest

from src.cli.command_parser import CommandParser, CommandSyntaxError
from src.cli.controller import Controller
from src.cli.result import OperationResult
from src.cli.view import View
from src.model.pir import PlainTextPIR
from tests.support import WorkspaceTestCase


class CommandParserTests(unittest.TestCase):
    def test_parser_handles_quoted_options_and_preserves_search_text(self) -> None:
        create = CommandParser.parse(
            'create task description="Confirm payment" deadline="2026-11-20 18:00"'
        )
        search = CommandParser.parse('search type = text && content contains "iPad Air"')

        self.assertEqual(create.name, "create")
        self.assertEqual(create.positionals, ("task",))
        self.assertEqual(create.options["description"], "Confirm payment")
        self.assertEqual(create.options["deadline"], "2026-11-20 18:00")
        self.assertEqual(search.argument_text, 'type = text && content contains "iPad Air"')

    def test_parser_rejects_unknown_commands_and_malformed_options(self) -> None:
        invalid_lines = (
            "",
            "unknown",
            "create",
            "update",
            "create text content",
            "create text content=one content=two",
            'create text content="unterminated',
        )
        for line in invalid_lines:
            with self.subTest(line=line):
                with self.assertRaises(CommandSyntaxError):
                    CommandParser.parse(line)


class ControllerTests(WorkspaceTestCase):
    def test_controller_supports_create_update_search_print_and_delete(self) -> None:
        controller = Controller()
        commands = [
            'create text content="title: iPad Air; status: available"',
            'create task description="Confirm payment" deadline="2026-11-20 18:00"',
            'create event description="Campus handover" start="2026-11-21 14:00" alarm="2026-11-21 13:30"',
            'create contact name="Chan Tai Man" address="Hung Hom" mobile="91234567"',
        ]
        results = [controller.execute(CommandParser.parse(command)) for command in commands]
        self.assertEqual([result.status for result in results], ["ok"] * 4)

        search = controller.execute(
            CommandParser.parse('search type = text && content contains "IPAD"')
        )
        self.assertEqual([record.id for record in search.records], [1])
        update = controller.execute(CommandParser.parse('update 1 content="status: sold"'))
        self.assertEqual(update.records[0].content, "status: sold")
        printed = controller.execute(CommandParser.parse("print all"))
        self.assertEqual([record.id for record in printed.records], [1, 2, 3, 4])
        deleted = controller.execute(CommandParser.parse("delete 4"))
        self.assertEqual(deleted.status, "ok")
        self.assertEqual([record.id for record in controller.repository.all()], [1, 2, 3])

    def test_controller_reports_errors_without_corrupting_repository(self) -> None:
        controller = Controller()
        controller.execute(CommandParser.parse('create text content="original"'))

        invalid_commands = (
            "create task description=missing",
            'update 1 status="sold"',
            "print abc",
            "delete 99",
            "save data.json",
            'search type = unsupported',
        )
        for line in invalid_commands:
            with self.subTest(line=line):
                result = controller.execute(CommandParser.parse(line))
                self.assertEqual(result.status, "error")
        self.assertEqual(controller.repository.get(1).content, "original")

    def test_controller_save_load_and_failed_load_are_safe(self) -> None:
        controller = Controller()
        controller.execute(CommandParser.parse('create text content="saved"'))
        path = self.artifact_path()
        path_text = path.as_posix()
        save = controller.execute(CommandParser.parse(f"save {path_text}"))
        self.assertEqual(save.status, "ok")
        controller.execute(CommandParser.parse('update 1 content="changed"'))

        load = controller.execute(CommandParser.parse(f"load {path_text}"))
        self.assertEqual(load.status, "ok")
        self.assertEqual(controller.repository.get(1).content, "saved")

        bad_path = self.artifact_path("bad.pim")
        bad_path.write_text("not json", encoding="utf-8")
        failed_load = controller.execute(CommandParser.parse(f"load {bad_path.as_posix()}"))
        self.assertEqual(failed_load.status, "error")
        self.assertEqual(controller.repository.get(1).content, "saved")

    def test_help_and_exit_results_are_available(self) -> None:
        controller = Controller()
        help_result = controller.execute(CommandParser.parse("help"))
        exit_result = controller.execute(CommandParser.parse("exit"))
        self.assertEqual(help_result.status, "help")
        self.assertIn("create text", help_result.message)
        self.assertEqual(exit_result.status, "exit")


class ViewTests(unittest.TestCase):
    def test_view_renders_each_result_kind(self) -> None:
        output = io.StringIO()
        view = View(output)
        record = PlainTextPIR(1, "listing")

        view.render_prompt()
        view.render(OperationResult("ok", "created PIR 1", (record,)))
        view.render(OperationResult("matches", "1 record(s) matched", (record,)))
        view.render(OperationResult("error", "bad command"))
        view.render(OperationResult("help", "help text"))
        view.render(OperationResult("exit"))

        rendered = output.getvalue()
        self.assertIn("pim> ", rendered)
        self.assertIn("OK: created PIR 1", rendered)
        self.assertIn("MATCHES: 1 record(s) matched", rendered)
        self.assertIn("ERROR: bad command", rendered)
        self.assertIn("help text", rendered)





