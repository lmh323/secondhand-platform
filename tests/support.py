"""Shared test helpers that keep artifacts inside the project workspace."""

from __future__ import annotations

import shutil
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class WorkspaceTestCase(unittest.TestCase):
    """Give each test a disposable directory under the project workspace."""

    def setUp(self) -> None:
        safe_name = self.id().replace(".", "_").replace("<", "_").replace(">", "_")
        self.test_directory = PROJECT_ROOT / "tmp" / "tests" / safe_name
        self.test_directory.mkdir(parents=True, exist_ok=True)
        self.addCleanup(self._remove_test_directory)

    def artifact_path(self, filename: str = "data.pim") -> Path:
        return self.test_directory / filename

    def _remove_test_directory(self) -> None:
        shutil.rmtree(self.test_directory, ignore_errors=True)

