# Hong Kong Student Second-hand PIM

This repository is the staged development workspace for the COMP3211 course project: a command-line Personal Information Management system themed around second-hand trading for university students in Hong Kong.

The product manages listing descriptions, buyer and seller contacts, transaction tasks, and handover events. It stores the records locally and simulates the transaction workflow. Actual payment and physical handover happen between the students outside the program.

The project is developed in gated stages. Each stage has its own requirements, design notes, implementation changes, tests, and acceptance record. The next stage starts only after the current stage is accepted.

## Current stage

Stage 6 submission package preparation - awaiting group-specific recordings and declaration completion.

## Implementation constraints

- Language: Python.
- Runtime dependencies: Python standard library only.
- Interface: command line.
- Architecture: Model-View-Controller (MVC), with all model code in the `model` package.
- Persistence: a `.pim` file containing a documented standard-library serialization format.
- Tests: automatically executable unit tests for the model, using `unittest` unless the requirements stage records a justified alternative.

## Repository layout

```text
secondhand-platform/
├── src/main.py             # CLI entry point
├── src/model/              # PIR types, search, repository, and persistence
├── src/cli/                # Command parsing, controller, and terminal view
├── tests/model/            # Unit tests for the system model
├── tools/                  # Verification, PDF, and ZIP build scripts
├── reports/                # Generated coverage and test reports
├── output/pdf/             # Generated submission PDFs
├── recordings/             # Group-recorded MP4 files
└── docs/                   # SRS, design, manuals, testing, and submission records
```

See [docs/00-project-skeleton.md](docs/00-project-skeleton.md) for the complete skeleton and [docs/01-development-roadmap.md](docs/01-development-roadmap.md) for the stage gates.

## Acceptance rule

At the end of each stage, the delivered documentation identifies the implemented scope, validation evidence, open risks, and the exact decision needed from the product owner. Development pauses at that gate until the stage is accepted.





