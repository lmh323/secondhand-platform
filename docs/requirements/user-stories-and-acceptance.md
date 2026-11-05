# User Stories and Acceptance Criteria

The following stories are the mandatory COMP3211 Appendix B stories expressed in the chosen second-hand trading scenario. Each acceptance criterion is observable and can be verified in the CLI or in a model unit test.

| ID | Story in this project | Acceptance criteria |
| --- | --- | --- |
| US1 | As a user, I want to create different types of PIRs so that I can manage all information about my trades in one place. | The user can create one Plain Text, Task, Event, and Contact PIR. Each receives a unique ID and can be printed. |
| US2 | As a user, I want to create a Plain Text PIR for a second-hand listing or note. | A non-empty text record is accepted, stored, assigned an ID, and printed with the exact content. |
| US3 | As a user, I want to create a Task PIR for a trade action with a deadline. | A task with a valid description and time is accepted; missing description or invalid time is rejected without adding a record. |
| US4 | As a user, I want to create an Event PIR for an inspection or handover with a start time and alarm. | An event with valid description, start, and alarm is accepted; invalid or missing time values are rejected. |
| US5 | As a user, I want to create a Contact PIR for a buyer or seller. | A contact with name, address, and mobile number is accepted and printed; any missing required field is rejected. |
| US6 | As a user, I want to modify an existing PIR so that a listing or plan stays up to date. | A valid update changes the requested field while preserving ID and type; an unknown ID or field produces an error and changes nothing. |
| US7 | As a user, I want to search PIRs using type, text, time, and logical criteria. | Type predicates, text `contains`, time `<`, `>`, `=`, parentheses, `!`, `&&`, and `||` work. Operator precedence is `!` then `&&` then `||`. Invalid criteria produce an error. |
| US8 | As a user, I want to print one PIR or all PIRs so that I can inspect the details of a trade. | `print <id>` shows every field of the selected record. `print all` shows every record in stable ID order. |
| US9 | As a user, I want to delete a selected PIR so that obsolete listings or plans are removed. | A valid ID is removed and is no longer searchable or printable. A missing ID produces an error and leaves other records unchanged. |
| US10 | As a user, I want to save my PIRs to a `.pim` file so that I can continue later. | A successful save creates or replaces a `.pim` file. Loading that file later reproduces all records and IDs. Non-`.pim` paths are rejected. |
| US11 | As a user, I want to load PIRs from a `.pim` file so that I can continue a previous trade-management session. | A valid file replaces the current repository with its records. A missing, malformed, or incompatible file produces an error and leaves the current repository unchanged. |

## End-to-end scenario for demonstration

1. Create a listing Plain Text PIR for an iPad.
2. Create a buyer Contact PIR.
3. Create a Task PIR for payment confirmation.
4. Create an Event PIR for campus handover.
5. Search for the listing by type and content.
6. Update its content from `status: available` to `status: sold` after the handover.
7. Print the listing and related records.
8. Save the repository to `campus_market.pim` and load it in a new session.
