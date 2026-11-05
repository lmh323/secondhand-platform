# Testing Workspace

Stage 5 adds automated unit and integration verification for the model and CLI boundaries.

## Test command

From the project root:

```powershell
python -m unittest discover -s tests -t . -v
```

The test suite uses Python's `unittest` module and stores temporary persistence files under the ignored `tmp/tests/` directory inside the project workspace.

## Coverage command

```powershell
python tools/coverage_report.py
```

The coverage runner uses Python's standard-library `trace` module. It runs the same test suite and writes reproducible artifacts to `reports/generated/`:

- `test-results.txt` — verbose test output;
- `coverage.txt` — per-file and total line coverage;
- `coverage.json` — machine-readable coverage data.

Package marker files named `__init__.py` are excluded from the line-coverage denominator. Branch coverage is outside the scope of this report.

## Requirements coverage

[Requirements coverage report](requirements-coverage.md) maps US1-US11 to concrete test methods and their latest result.

[Stage 5 delivery record](stage-5-delivery.md) records the accepted scope, validation evidence, known limitations, and the next stage gate.
