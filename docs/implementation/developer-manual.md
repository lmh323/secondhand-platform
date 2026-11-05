# Developer Manual

Status: Final submission version

## Development environment

- Platform: Windows with PowerShell.
- Python: Python 3.12.7 was used for validation. Python 3.11 or later is the target range.
- Dependencies: Python standard library only.
- Working directory: the `secondhand-platform` project root.

## Run the program

From the project root:

```powershell
python -m src.main
```

The program displays `pim>` and reads one command per line. Type `help` to display the supported command formats. Type `exit` or send end-of-file to end the session.

## Compile check

```powershell
python -m compileall -q .\src
```

## Debug the program

Run the module under Python's standard debugger:

```powershell
python -m pdb -m src.main
```

In an IDE, use `src.main` as the module entry point and set the working directory to the project root.

## Source layout

- `src/model`: PIR entities, repository, criteria, persistence, and model errors.
- `src/cli/command_parser.py`: tokenization and command shape validation.
- `src/cli/controller.py`: application use cases and model error conversion.
- `src/cli/view.py`: terminal output.
- `src/main.py`: dependency wiring and command loop.

The model package has no dependency on the CLI. This keeps model tests independent of terminal input and output.

## Design constraints

Use only Python standard-library modules. Keep business rules in `src/model`, keep terminal formatting in `src/cli/view.py`, and update the requirements traceability matrix when a feature changes.
