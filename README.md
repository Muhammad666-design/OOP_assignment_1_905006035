# Community Repair and Reuse Management System

A menu-driven Python prototype for organising repair requests at a small
community repair centre. It uses object-oriented classes and only the Python
standard library.

## Requirements

- Python 3.8 or later
- No third-party packages

## Run the application

Open a terminal in this folder and run:

```text
python main.py
```

Choose a menu number to register a repair request, view or search requests,
register and view technicians, assign a technician, update a status, or record
an outcome. Enter `0` to exit.

The application stores requests and technicians in dictionaries while it is
running. Data is held in memory and is lost when the program exits.

## Run tests

```text
python -m unittest discover -s tests -v
```

The tests cover request and technician registration, identifier lookup,
technician assignment, status validation, outcome recording, and the menu
workflow.

## Repair statuses

- New
- In Progress
- Awaiting Parts
- Completed
- Reuse Assessment

Status input is matched without regard to letter case; the application stores
the standard capitalization shown above.

## Privacy and intended use

This is an educational prototype, not a production system. It has no login,
access controls, persistent storage, or security review. Use fictional data in
demonstrations and do not store sensitive personal information.
