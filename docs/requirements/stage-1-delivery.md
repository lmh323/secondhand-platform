# Stage 1 Delivery Record

Status: Ready for user acceptance

## Delivered

- Defined the single-user second-hand trade-management scope.
- Mapped all mandatory US1-US11 stories to functional requirements.
- Defined the four PIR types and the listing content template.
- Defined the proposed CLI commands, input formats, error behavior, and search grammar.
- Defined non-functional requirements for standard-library implementation, model separation, reliability, persistence, determinism, usability, performance, testability, and local privacy.
- Created a traceability matrix for the later implementation and test reports.

## Decisions made

- The graded product is a local command-line PIM, not a networked marketplace.
- A second-hand listing is stored in a Plain Text PIR; a separate custom Listing PIR is not required.
- The actual trade workflow is represented by a listing, contacts, tasks, and events.
- The user can save and load a repository through `.pim` files.

## Open items for the design stage

- Final Python version and documented development platform.
- Exact class fields, public methods, and exception types.
- Exact `.pim` JSON schema and versioning field.
- Detailed MVC component relationships and diagrams.
- Final parser implementation strategy and test data.

## Acceptance gate

Stage 1 is ready for acceptance when the product owner agrees that:

1. The single-user command-line scope is correct.
2. The four PIR types and the listing representation are correct.
3. The command names and search grammar are suitable for the project.
4. All required US1-US11 stories are represented.
5. Stage 2 may begin with the listed open items.
