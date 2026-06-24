# Expense Tracker CLI

A simple Python command-line expense tracker that stores spending records in a local SQLite database.

## Description

This project is a terminal-based expense tracker built in Python. It lets you:

* add a new expense with amount, category, optional reason, and optional date
* list saved expenses with optional category and month filters
* delete an expense by ID
* view a spending summary with optional month filtering

The tool uses Python's standard library only and stores data in `expenses.db`.

## Getting Started

### Requirements

* Python 3.10 or newer
* No additional third-party packages required

### Installing

1. Open a terminal in the project folder.
2. (Optional) Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

3. No external dependencies are required, so you can run the script directly.

### Running the CLI

From the project directory, run:

```powershell
python tracker.py <command> [options]
```

### Commands

* `add <amount> <category> [reason] [-d DATE]`
  * Adds a new expense.
  * Example: `python tracker.py add 12.50 food lunch -d 2026-06-23`
* `list [--category CATEGORY] [--month YYYY-MM]`
  * Lists saved expenses, optionally filtered by category or month.
  * Example: `python tracker.py list --month 2026-06`
* `delete <id>`
  * Deletes the expense with the given ID.
  * Example: `python tracker.py delete 3`
* `summary [--month YYYY-MM]`
  * Prints total spending and a category breakdown, optionally filtered by month.
  * Example: `python tracker.py summary --month 2026-06`

### Notes

* Amount must be greater than 0.
* Category must not be empty.
* If no date is provided when adding an expense, the current local date is used.
* The `--month` filter expects `YYYY-MM` format.

## Database

The project uses a local SQLite database file named `expenses.db`.

If the database file does not exist, it is created automatically when the script runs.

## License

This project is licensed under the [MIT License](LICENSE).
