# Stage 0 Scope and Assumptions

Status: Revised for COMP3211 and ready for acceptance

## Product goal

Build a command-line Personal Information Management (PIM) system for Hong Kong university students who manage second-hand trades. The system records the information needed for a trade and guides a single user through a local transaction workflow.

The system is a transaction information manager. It does not provide network accounts, a shared online marketplace, payment processing, delivery integration, or real-time chat because the course brief requires a command-line PIM and says online support and GUI work are not recommended.

## How a trade is represented

The program models a complete example trade with the mandatory PIR types:

1. A **Plain Text PIR** stores the listing title, category, condition, asking price, availability, and description.
2. A **Contact PIR** stores the buyer or seller name, address, and mobile number.
3. A **Task PIR** stores actions such as confirming payment or preparing the item, with a deadline.
4. An **Event PIR** stores an inspection or campus handover time and alarm.
5. The user searches and modifies the records, prints the details, marks the listing as sold in its text record, and saves the whole set to a `.pim` file.

The actual payment and handover can be arranged by phone or in person. The project demonstrates how the system manages the records and state changes around that trade.

## Assignment-safe boundary

- Support every required user story US1-US11 from Appendix B.
- Keep all model code in a separate `model` package.
- Use Python standard libraries only.
- Provide a clear command format, validation errors, and output format.
- Do not spend implementation time on a GUI, web server, online user accounts, or external services.
- Treat any future web interface as a separate extension that is outside the graded core.

## Assumptions to validate in Stage 1

- One local user manages the records in each program session.
- A listing is represented by a plain-text PIR; a new custom Listing PIR type is not needed for the required user stories.
- A stable PIR identifier is generated so a user can modify, print, or delete one record.
- The `.pim` format will use a documented standard-library serialization, most likely JSON content with a `.pim` extension.
- Search will implement text containment, time comparisons `<`, `>`, and `=`, and logical connectors `&&`, `||`, and `!` exactly as required by US7.
