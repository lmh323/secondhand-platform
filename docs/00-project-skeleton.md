# Project Engineering Skeleton

This document records the assignment-safe engineering layout. The implementation keeps the model and CLI boundaries explicit while allowing each stage to add its own verification and submission records.

```text
secondhand-platform/
├── README.md
├── .gitignore
├── docs/
│   ├── 00-scope-and-assumptions.md
│   ├── 00-project-skeleton.md
│   ├── 01-development-roadmap.md
│   ├── adr/
│   ├── requirements/
│   ├── design/
│   ├── implementation/
│   ├── testing/
│   └── submission/
├── src/
│   ├── main.py
│   ├── cli/
│   │   ├── command_parser.py
│   │   ├── controller.py
│   │   ├── result.py
│   │   └── view.py
│   └── model/
│       ├── pir.py
│       ├── criteria.py
│       ├── errors.py
│       ├── repository.py
│       ├── persistence.py
│       └── time_utils.py
├── tests/
│   ├── model/
│   ├── cli/
│   └── test_main.py
├── tools/
│   └── coverage_report.py
├── reports/
└── deliverables/
```

## Directory ownership

| Directory | Responsibility | First populated in |
| --- | --- | --- |
| `src/model` | PIR entities, validation, search criteria, repository, and `.pim` persistence | Stage 3 |
| `src/cli` | Command parsing, controller use cases, result values, and terminal output | Stage 4 |
| `src/main.py` | Program entry point and dependency wiring | Stage 4 |
| `tests/model` | Automatically executable model unit tests | Stage 5 |
| `tests/cli` and `tests/test_main.py` | CLI and command-loop verification | Stage 5 |
| `tools` | Reproducible standard-library verification scripts | Stage 5 |
| `reports` | Generated coverage and test reports | Stage 5 |
| `docs/requirements` | SRS, user stories, and acceptance criteria | Stage 1 |
| `docs/design` | MVC, class, relationship, and sequence/activity diagrams | Stage 2 |
| `docs/implementation` | Developer, user, and stage implementation records | Stage 4 |
| `docs/testing` | Test strategy and verification evidence | Stage 5 |
| `docs/submission` | Video, presentation, and final ZIP checklist | Stage 6 |
| `deliverables` | Final copies of required submission files | Stage 6 |

## Boundary rules

- `src/model` contains no terminal input/output code.
- `src/cli` delegates business decisions to the model and formats results for the user.
- The model exposes operations for create, modify, search, print, delete, save, and load.
- The persistence layer owns the `.pim` representation.
- Every stage adds or updates its development documents before delivery.
