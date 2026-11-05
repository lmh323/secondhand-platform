# Stage 3 Model Implementation Delivery

Status: Ready for user acceptance

## Implemented

The model layer now contains:

- `PIR` as the common abstract record interface;
- `PlainTextPIR`, `TaskPIR`, `EventPIR`, and `ContactPIR`;
- validation and stable model exceptions;
- `PIRRepository` for ID allocation, create, get, update, search, delete, list, and replacement operations;
- `CriterionParser` and the criterion tree for type, text, time, negation, conjunction, disjunction, and parentheses;
- `PIMSerializer` and `PIRFactory` for version 1 JSON-based `.pim` files;
- date and time conversion for user input and persistence output;
- package exports through `src/model/__init__.py`.

## Files

- [model package](../../src/model/__init__.py)
- [PIR entities](../../src/model/pir.py)
- [search criteria](../../src/model/criteria.py)
- [repository](../../src/model/repository.py)
- [persistence](../../src/model/persistence.py)
- [model errors](../../src/model/errors.py)

## Behavior delivered

- New records receive positive, unique integer IDs.
- Updates validate every requested field before applying changes.
- Search results are sorted by ID.
- Text `contains` searches are case-insensitive.
- Missing fields do not match a predicate; unknown search fields are rejected.
- Save and load preserve record types, IDs, fields, and time values.
- `.pim` saves use a temporary file and replace the target after serialization succeeds.
- Invalid `.pim` fields, schema versions, duplicate IDs, and time values are rejected.

## Validation performed

The source was compiled with Python 3.12.7 using:

```powershell
$env:PYTHONPATH = "S:\comp2027\comp3211\secondhand-platform\src"
python -m compileall -q .\secondhand-platform\src
```

A smoke check then created all four PIR types, searched for a case-insensitive text match, updated the listing status, rejected an unknown update field, saved and loaded a workspace `.pim` file, and rejected a non-`.pim` path. It passed with the message `stage-3 smoke test passed`.

Formal unit-test files are scheduled for Stage 5 so they can be written against the accepted model interfaces and reported with coverage.

## Stage gate

Stage 3 is ready for acceptance when the product owner agrees that:

1. The four PIR implementations represent the approved trade records.
2. Repository update, search, delete, and replacement behavior is correct.
3. The search parser and case-insensitive text behavior are suitable.
4. The `.pim` schema and validation rules are acceptable.
5. Stage 4 may begin with CLI integration.
