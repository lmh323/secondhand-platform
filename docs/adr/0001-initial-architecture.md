# ADR 0001 Initial Architecture

Status: Proposed for COMP3211

## Context

The course project requires a command-line Personal Information Management system. The model must support four PIR types, record search criteria, modification, printing, deletion, and `.pim` persistence. The model also needs to be independently unit tested.

## Decision

Use a small object-oriented MVC design in Python with standard libraries only:

- **Model:** PIR base type, Plain Text, Task, Event, Contact, search criteria, repository, validation, and persistence.
- **View:** terminal output and prompts.
- **Controller:** command parsing and coordination of model operations.
- **Entry point:** `src/main.py` wires the controller, view, repository, and persistence components.

The `.pim` file will store a documented serialization of the repository. The exact schema and command syntax are finalized in Stage 1 and Stage 2.

## Why this decision

- It directly matches the command-line PIM requirement.
- The model can be tested without terminal input or output.
- The design keeps parsing, business rules, and persistence separate.
- The four required PIR types can be extended without changing the controller contract.
- Python's standard library is sufficient for the planned implementation.

## Alternatives considered

- A web client and server would add online features that the course brief does not require and does not reward with extra credit.
- A procedural design is allowed, but the object-oriented structure makes PIR polymorphism and unit testing easier to explain.

## Consequences

The program manages and simulates a trade rather than connecting two remote users. A listing, contact, task, and handover event can be created and updated locally; payment and physical exchange are arranged outside the program. The system remains useful for demonstrating the required search, update, persistence, and testing behavior.
