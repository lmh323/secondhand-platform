# Staged Development Roadmap

The project uses gated delivery. A stage is complete only when its implementation and its development records are delivered and the product owner accepts the stage.

| Stage | Focus | Main deliverables | Acceptance evidence |
| --- | --- | --- | --- |
| 0 | Scope and skeleton | Assignment-safe scope, repository layout, MVC boundary, stage plan | PIR mapping and course constraints reviewed |
| 1 | Requirements | SRS, user stories US1-US11, command grammar, acceptance criteria, non-functional requirements | Every required story has a testable criterion |
| 2 | Design | MVC architecture diagram, class and relationship diagrams, search/update sequence or activity diagram | Main use cases can be traced through the components |
| 3 | Model implementation | PIR classes, validation, search criteria, repository, `.pim` save/load | Model operations run independently of the CLI |
| 4 | CLI integration | Command parser, controller, view, invalid-input handling, developer manual, user manual | A user can complete the approved trade workflow from the terminal |
| 5 | Verification and reports | Model unit tests, line coverage report, requirements coverage report, test documentation | Tests run automatically and evidence is reproducible |
| 6 | Submission package | Video script and recording, presentation slides and recording, Honour Declaration, final ZIP checklist | All required files and formats are checked |

## Stage gate format

Every delivery should include:

- the scope implemented in the stage;
- changed files and design decisions;
- commands used to run and validate it;
- test results and known limitations;
- updated documentation;
- the exact acceptance decision required before the next stage.

## Working rule

The product owner may request changes at a stage gate. Those changes are incorporated into the current stage and re-delivered before the next stage begins. No later-stage feature is implemented just to anticipate approval.
