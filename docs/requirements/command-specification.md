# Command Specification

Status: Stage 1 baseline proposal

The prompt is `pim>`. The command parser shall accept one command per line. Values containing spaces shall be enclosed in double quotes. Backslash escaping follows Python's standard `shlex` rules.

## Commands

| Command | Purpose | Example |
| --- | --- | --- |
| `create text content="..."` | Create a Plain Text PIR | `create text content="title: iPad Air; status: available"` |
| `create task description="..." deadline="YYYY-MM-DD HH:MM"` | Create a Task PIR | `create task description="Confirm payment" deadline="2026-11-20 18:00"` |
| `create event description="..." start="YYYY-MM-DD HH:MM" alarm="YYYY-MM-DD HH:MM"` | Create an Event PIR | `create event description="Campus handover" start="2026-11-21 14:00" alarm="2026-11-21 13:30"` |
| `create contact name="..." address="..." mobile="..."` | Create a Contact PIR | `create contact name="Chan Tai Man" address="Hung Hom" mobile="91234567"` |
| `update <id> field="value"` | Modify one field of an existing PIR | `update 1 content="title: iPad Air; status: sold"` |
| `search <criterion>` | Search the repository | `search type = text && content contains "iPad"` |
| `print <id>` | Print one detailed PIR | `print 1` |
| `print all` | Print all detailed PIRs | `print all` |
| `delete <id>` | Delete one PIR | `delete 4` |
| `save <file.pim>` | Save the repository | `save campus_market.pim` |
| `load <file.pim>` | Replace the repository with a saved file | `load campus_market.pim` |
| `help` | Print command help | `help` |
| `exit` | End the session | `exit` |

## Field rules

- `text` accepts only `content`.
- `task` accepts only `description` and `deadline`.
- `event` accepts only `description`, `start`, and `alarm`.
- `contact` accepts only `name`, `address`, and `mobile`.
- Required text values cannot be empty after trimming whitespace.
- Time values use `YYYY-MM-DD HH:MM` and represent Hong Kong local time.
- `<file.pim>` must end in `.pim`, case-insensitively.
- The user cannot choose or overwrite a PIR ID through a create command.

## Search grammar

The following grammar is the Stage 1 baseline:

```text
criterion       := disjunction
disjunction     := conjunction ("||" conjunction)*
conjunction     := negation ("&&" negation)*
negation        := "!" negation | primary
primary         := predicate | "(" criterion ")"

predicate       := "type" "=" type_name
                 | text_field "contains" quoted_text
                 | time_field time_operator quoted_time

type_name       := "text" | "task" | "event" | "contact"
text_field      := "content" | "description" | "name" | "address" | "mobile"
time_field      := "deadline" | "start" | "alarm"
time_operator   := "<" | ">" | "="
```

The precedence is `!`, then `&&`, then `||`. Parentheses can override the default precedence. A record without the requested field does not match that predicate. An unknown field or malformed literal is an error.

## Result and error format

- Successful create, update, delete, save, and load commands begin with `OK:`.
- Search results begin with `MATCHES:` and list matching IDs before their details.
- Printed records show the ID, type, and every type-specific field.
- Invalid input begins with `ERROR:` and includes the expected format when it can be identified.
- The program shall continue accepting commands after a recoverable error.
