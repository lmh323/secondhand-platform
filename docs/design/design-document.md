# Design Document

Status: Final submission baseline  
Version: 1.0  
System: Hong Kong Student Second-hand PIM

## 1 Design goals

The design turns the Stage 1 requirements into a small, testable command-line application. It keeps the domain model independent from terminal input and output, gives every PIR type a consistent interface, and makes search and persistence replaceable components.

The design targets Python 3.11 or later and Python standard libraries only. The final developer manual will record the exact Python version and documented development platform.

## 2 Architectural pattern

The system uses Model-View-Controller (MVC).

- **Model** owns PIR data, validation, search evaluation, repository operations, and `.pim` serialization.
- **View** owns prompts and human-readable terminal output.
- **Controller** receives parsed commands, invokes model operations, and converts domain errors into operation results.

MVC is suitable because the model must be unit tested without simulating terminal input. It also keeps command syntax changes in the CLI layer and protects the model from presentation details.

```mermaid
flowchart LR
    U[Single local user] --> V[View\nterminal input and output]
    V --> CP[CommandParser\nsyntax validation]
    CP --> C[Controller\nuse-case coordination]
    C --> R[PIRRepository\nrecords and IDs]
    C --> Q[CriterionParser\nsearch expression]
    C --> S[PIMSerializer\n.pim files]
    R --> P[PIR hierarchy\nText / Task / Event / Contact]
    Q --> P
    S --> F[(Local .pim file)]
```

The model never imports the CLI package. The controller is the only component that coordinates the repository, criterion parser, and serializer for a user command.

## 3 Main component relationships

```mermaid
flowchart TB
    subgraph CLI
        Main[src/main.py]
        Parser[src/cli/command_parser.py]
        Controller[src/cli/controller.py]
        View[src/cli/view.py]
        Result[src/cli/result.py]
    end

    subgraph MODEL
        Repo[src/model/repository.py]
        PIR[src/model/pir.py]
        Types[PlainTextPIR / TaskPIR / EventPIR / ContactPIR]
        Criteria[src/model/criteria.py]
        Persistence[src/model/persistence.py]
        Errors[src/model/errors.py]
    end

    Main --> View
    Main --> Controller
    View --> Parser
    Parser --> Controller
    Controller --> Result
    Controller --> Repo
    Controller --> Criteria
    Controller --> Persistence
    Repo --> PIR
    PIR --> Types
    Repo --> Errors
    Criteria --> PIR
    Criteria --> Errors
    Persistence --> Types
    Persistence --> Errors
    Result --> View
```

### Component responsibilities

| Component | Responsibility | Depends on |
| --- | --- | --- |
| `main.py` | Create objects and run the command loop | CLI components |
| `CommandParser` | Convert one input line into a typed command | `shlex`, command errors |
| `Controller` | Execute create, update, search, print, delete, save, load, help, and exit | Model components, result type |
| `View` | Display prompts, success output, records, and errors | Result type |
| `PIRRepository` | Allocate IDs, store records, update records, search, and delete | PIR hierarchy, criteria |
| PIR hierarchy | Validate and represent record-specific fields | Python standard library |
| `CriterionParser` | Parse the search grammar into a criterion tree | Criterion classes, PIR field names |
| Criterion classes | Evaluate predicates and logical operators | PIR interface |
| `PIMSerializer` | Validate `.pim` paths and round-trip records | `json`, `pathlib`, PIR factory |
| Domain errors | Give callers stable error categories | `Exception` |

## 4 Domain class design

```mermaid
classDiagram
    class PIR {
        <<abstract>>
        +int id
        +str type_name
        +allowed_fields() frozenset~str~
        +get_field(name: str) object
        +update(changes: Mapping) None
        +to_dict() dict
        +format_details() str
    }

    class PlainTextPIR {
        +str content
        +allowed_fields() frozenset~str~
        +get_field(name: str) object
        +update(changes: Mapping) None
        +to_dict() dict
        +format_details() str
    }

    class TaskPIR {
        +str description
        +datetime deadline
        +allowed_fields() frozenset~str~
        +get_field(name: str) object
        +update(changes: Mapping) None
        +to_dict() dict
        +format_details() str
    }

    class EventPIR {
        +str description
        +datetime start
        +datetime alarm
        +allowed_fields() frozenset~str~
        +get_field(name: str) object
        +update(changes: Mapping) None
        +to_dict() dict
        +format_details() str
    }

    class ContactPIR {
        +str name
        +str address
        +str mobile
        +allowed_fields() frozenset~str~
        +get_field(name: str) object
        +update(changes: Mapping) None
        +to_dict() dict
        +format_details() str
    }

    PIR <|-- PlainTextPIR
    PIR <|-- TaskPIR
    PIR <|-- EventPIR
    PIR <|-- ContactPIR
```

### Shared PIR contract

| Method | Signature | Return | Exceptions |
| --- | --- | --- | --- |
| `allowed_fields` | `allowed_fields() -> frozenset[str]` | Fields valid for the concrete type | None |
| `get_field` | `get_field(name: str) -> object \| None` | Field value, or `None` when the record has no such field | `ValidationError` for an unknown field name |
| `update` | `update(changes: Mapping[str, object]) -> None` | None | `ValidationError` if a field is unknown, empty, or has the wrong type |
| `to_dict` | `to_dict() -> dict[str, Any]` | Serializable record data | None after a valid object exists |
| `format_details` | `format_details() -> str` | Stable human-readable details | None |

Constructors validate IDs, required strings, and time values. Date and time fields are stored as `datetime` objects in memory and serialized as `YYYY-MM-DDTHH:MM` strings.

### Concrete PIR fields

| Class | Constructor | `type_name` | Allowed fields |
| --- | --- | --- | --- |
| `PlainTextPIR` | `(id: int, content: str)` | `text` | `content` |
| `TaskPIR` | `(id: int, description: str, deadline: datetime)` | `task` | `description`, `deadline` |
| `EventPIR` | `(id: int, description: str, start: datetime, alarm: datetime)` | `event` | `description`, `start`, `alarm` |
| `ContactPIR` | `(id: int, name: str, address: str, mobile: str)` | `contact` | `name`, `address`, `mobile` |

## 5 Repository design

`PIRRepository` stores records in a private dictionary keyed by ID. It returns records in ascending ID order for `all` and `search` so output is deterministic.

| Method | Signature | Return | Exceptions |
| --- | --- | --- | --- |
| `create_plain_text` | `(content: str) -> PlainTextPIR` | New record | `ValidationError` |
| `create_task` | `(description: str, deadline: datetime) -> TaskPIR` | New record | `ValidationError` |
| `create_event` | `(description: str, start: datetime, alarm: datetime) -> EventPIR` | New record | `ValidationError` |
| `create_contact` | `(name: str, address: str, mobile: str) -> ContactPIR` | New record | `ValidationError` |
| `get` | `(record_id: int) -> PIR` | Existing record | `PIRNotFoundError` |
| `update` | `(record_id: int, changes: Mapping[str, object]) -> PIR` | Updated record | `PIRNotFoundError`, `ValidationError` |
| `search` | `(criterion: Criterion) -> list[PIR]` | Matching records | None after criterion validation |
| `all` | `() -> list[PIR]` | All records in ID order | None |
| `delete` | `(record_id: int) -> None` | None | `PIRNotFoundError` |
| `replace` | `(records: Sequence[PIR]) -> None` | None | `ValidationError` for duplicate or invalid IDs |

`update` validates all changes before mutating the record. If one field is invalid, no field from the update is applied.

## 6 Search design

The criterion parser converts the Stage 1 grammar into a tree of `Criterion` objects.

```mermaid
classDiagram
    class Criterion {
        <<abstract>>
        +evaluate(record: PIR) bool
    }
    class PredicateCriterion {
        +str field
        +str operator
        +object value
        +evaluate(record: PIR) bool
    }
    class NotCriterion {
        +Criterion operand
        +evaluate(record: PIR) bool
    }
    class AndCriterion {
        +Criterion left
        +Criterion right
        +evaluate(record: PIR) bool
    }
    class OrCriterion {
        +Criterion left
        +Criterion right
        +evaluate(record: PIR) bool
    }
    class CriterionParser {
        +parse(expression: str) Criterion
    }
    Criterion <|-- PredicateCriterion
    Criterion <|-- NotCriterion
    Criterion <|-- AndCriterion
    Criterion <|-- OrCriterion
    CriterionParser ..> Criterion
```

| Class or method | Signature | Return | Exceptions |
| --- | --- | --- | --- |
| `Criterion.evaluate` | `(record: PIR) -> bool` | Whether the record matches | `ValidationError` only for an invalid constructed criterion |
| `PredicateCriterion` | `(field: str, operator: str, value: object)` | Criterion object | `ValidationError` for unsupported field/operator/value |
| `CriterionParser.parse` | `(expression: str) -> Criterion` | Parsed criterion tree | `CriterionParseError` |

The parser enforces precedence `!`, then `&&`, then `||`. Text `contains` comparisons are case-insensitive. A missing field on a concrete PIR evaluates to `False`; an unknown field in the expression is a parse error.

## 7 Persistence design

`PIMSerializer` is the only class that reads or writes `.pim` files.

| Method | Signature | Return | Exceptions |
| --- | --- | --- | --- |
| `save` | `save(records: Sequence[PIR], path: Path) -> None` | None | `PersistenceError`, `ValidationError` |
| `load` | `load(path: Path) -> list[PIR]` | Validated records | `PersistenceError`, `ValidationError` |

The Stage 2 schema is:

```json
{
  "schema_version": 1,
  "records": [
    {"id": 1, "type": "text", "content": "..."},
    {"id": 2, "type": "task", "description": "...", "deadline": "2026-11-20T18:00"}
  ]
}
```

The serializer rejects a non-`.pim` path, a missing required top-level key, an unsupported schema version, duplicate IDs, unknown types, invalid fields, and invalid time strings. It writes through a temporary file and replaces the target only after serialization succeeds.

## 8 CLI design

```mermaid
classDiagram
    class Command {
        +str name
        +tuple~str~ positionals
        +dict~str,str~ options
    }
    class CommandParser {
        +parse(line: str) Command
    }
    class OperationResult {
        +str status
        +str message
        +tuple~PIR~ records
    }
    class Controller {
        +execute(command: Command) OperationResult
    }
    class View {
        +render(result: OperationResult) None
        +render_help() None
    }
    CommandParser --> Command
    Controller --> Command
    Controller --> OperationResult
    View --> OperationResult
```

| Class or method | Signature | Return | Exceptions |
| --- | --- | --- | --- |
| `CommandParser.parse` | `(line: str) -> Command` | Parsed command | `CommandSyntaxError` |
| `Controller.execute` | `(command: Command) -> OperationResult` | Result for the view | Catches domain errors and returns `error` status |
| `View.render` | `(result: OperationResult) -> None` | None | None for valid result objects |
| `main.run` | `() -> None` | None | Handles end-of-input and clean exit |

`Controller.execute` maps `PIMError` subclasses into `OperationResult(status="error", ...)`. The CLI loop therefore continues after recoverable input errors and never exposes a Python traceback during normal use.

## 9 Example use: search then update

The sequence below satisfies the design-document example-use requirement.

```mermaid
sequenceDiagram
    actor User
    participant View
    participant Parser as CommandParser
    participant Controller
    participant Criteria as CriterionParser
    participant Repo as PIRRepository
    participant Record as PlainTextPIR

    User->>View: Enter search type = text && content contains "iPad"
    View->>Parser: parse(line)
    Parser-->>View: Command(search, expression)
    View->>Controller: execute(command)
    Controller->>Criteria: parse(expression)
    Criteria-->>Controller: Criterion tree
    Controller->>Repo: search(criterion)
    Repo->>Record: evaluate(criterion)
    Record-->>Repo: true or false
    Repo-->>Controller: matching PIRs in ID order
    Controller-->>View: OperationResult(matches, records)
    View-->>User: Print matching IDs and details

    User->>View: Enter update 1 content="... status: sold ..."
    View->>Parser: parse(line)
    Parser-->>View: Command(update, id, changes)
    View->>Controller: execute(command)
    Controller->>Repo: get(1)
    Repo-->>Controller: PlainTextPIR #1
    Controller->>Record: update(changes)
    Record-->>Controller: updated record
    Controller->>Repo: retain updated record
    Controller-->>View: OperationResult(ok, updated)
    View-->>User: Print update confirmation
```

## 10 Design-to-requirements mapping

| Requirement area | Design element |
| --- | --- |
| US1-US5 | PIR hierarchy and repository create methods |
| US6 | `PIR.update` and repository atomic update |
| US7 | `CriterionParser` and criterion tree |
| US8-US9 | Repository `all`, `get`, and `delete`; View formatting |
| US10-US11 | `PIMSerializer` and repository `replace` |
| Model unit tests | Model has no CLI dependency |
| Standard library | Python classes, `datetime`, `json`, `pathlib`, `shlex`, and `typing` |

