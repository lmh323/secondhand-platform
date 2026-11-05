# Stage 2 Delivery Record

Status: Ready for user acceptance

## Delivered

- Selected and justified MVC for the command-line PIM.
- Defined the Model, View, Controller, repository, criterion parser, serializer, and error boundaries.
- Defined the four PIR subclasses and their fields.
- Defined public methods, argument types, return types, and expected exceptions for the main components.
- Defined the `.pim` JSON schema and round-trip behavior.
- Added architecture, component, class, criterion, and search/update sequence diagrams.
- Mapped the design back to US1-US11 and the model-testing requirement.

## Decisions for implementation

- Python 3.11 or later is the target language/runtime range.
- The application uses a local MVC command loop.
- The repository owns IDs and deterministic record ordering.
- Updates are atomic: invalid changes leave the target PIR unchanged.
- Search expressions are parsed into a criterion tree with precedence `!`, `&&`, then `||`.
- `.pim` files use schema version 1 and JSON content.

## Stage gate

Stage 2 is ready for acceptance when the product owner agrees that:

1. The MVC boundaries are clear.
2. The class and method interfaces are sufficient to begin model implementation.
3. The `.pim` schema is acceptable.
4. The search and update sequence reflects the intended user experience.
5. Stage 3 may begin with model implementation.
