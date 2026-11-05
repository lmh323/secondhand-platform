"""Run the unit suite and produce a standard-library line coverage report."""

from __future__ import annotations

import json
import sys
import trace
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "generated"
COVERAGE_DIR = REPORT_DIR / "coverage"


def _normalise(path: str | Path) -> Path:
    candidate = Path(path).resolve()
    if candidate.suffix == ".pyc":
        candidate = candidate.with_suffix(".py")
    return candidate


def _run_tests() -> tuple[unittest.TestResult, str]:
    suite = unittest.defaultTestLoader.discover(
        start_dir=str(ROOT / "tests"),
        pattern="test*.py",
        top_level_dir=str(ROOT),
    )
    import io

    output = io.StringIO()
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    return result, output.getvalue()


def _coverage_rows(counts: dict[tuple[str, int], int]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in sorted((ROOT / "src").rglob("*.py")):
        if source.name == "__init__.py":
            continue
        executable = {
            line
            for line in trace._find_executable_linenos(str(source))
            if isinstance(line, int) and line > 0
        }
        if not executable:
            continue
        source_key = _normalise(source)
        covered = {
            line
            for (filename, line), count in counts.items()
            if count and _normalise(filename) == source_key and line in executable
        }
        missing = sorted(executable - covered)
        rows.append(
            {
                "file": str(source.relative_to(ROOT)).replace("\\", "/"),
                "executable_lines": len(executable),
                "covered_lines": len(covered),
                "coverage_percent": round(100 * len(covered) / len(executable), 1),
                "missing_lines": missing,
            }
        )
    return rows


def _write_reports(result: unittest.TestResult, test_output: str, rows: list[dict[str, Any]]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    COVERAGE_DIR.mkdir(parents=True, exist_ok=True)

    (REPORT_DIR / "test-results.txt").write_text(test_output, encoding="utf-8")
    (REPORT_DIR / "coverage.json").write_text(
        json.dumps(
            {
                "tool": "python trace",
                "tests_run": result.testsRun,
                "failures": len(result.failures),
                "errors": len(result.errors),
                "files": rows,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    total_executable = sum(row["executable_lines"] for row in rows)
    total_covered = sum(row["covered_lines"] for row in rows)
    total_percent = 100 * total_covered / total_executable if total_executable else 100.0
    lines = [
        "Stage 5 line coverage report",
        "Coverage engine: Python standard-library trace module",
        f"Tests run: {result.testsRun}",
        f"Failures: {len(result.failures)}",
        f"Errors: {len(result.errors)}",
        "",
        "file | covered / executable | coverage | missing lines",
    ]
    for row in rows:
        missing = ", ".join(str(line) for line in row["missing_lines"]) or "-"
        lines.append(
            f"{row['file']} | {row['covered_lines']} / {row['executable_lines']} "
            f"| {row['coverage_percent']:.1f}% | {missing}"
        )
    lines.extend(
        [
            "",
            f"TOTAL | {total_covered} / {total_executable} | {total_percent:.1f}%",
        ]
    )
    (REPORT_DIR / "coverage.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    sys.path.insert(0, str(ROOT))
    ignoredirs = [str(Path(sys.prefix).resolve()), str(Path(sys.exec_prefix).resolve())]
    tracer = trace.Trace(count=True, trace=False, ignoredirs=ignoredirs)
    result, test_output = tracer.runfunc(_run_tests)
    rows = _coverage_rows(tracer.results().counts)
    _write_reports(result, test_output, rows)
    print(test_output, end="")
    total_executable = sum(row["executable_lines"] for row in rows)
    total_covered = sum(row["covered_lines"] for row in rows)
    total_percent = 100 * total_covered / total_executable if total_executable else 100.0
    print(f"Coverage report: {total_covered}/{total_executable} lines ({total_percent:.1f}%)")
    print(f"Reports: {REPORT_DIR}")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())


