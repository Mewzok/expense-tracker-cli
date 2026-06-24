import argparse
import sqlite3
from datetime import datetime

DB_PATH = "expenses.db"


def positive_amount(value):
    try:
        amount = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError("Amount must be a number.")
    if amount <= 0:
        raise argparse.ArgumentTypeError("Amount must be greater than 0.")
    return amount


def non_empty_string(value):
    text = value.strip()
    if not text:
        raise argparse.ArgumentTypeError("Value must not be empty.")
    return text


def valid_date(value):
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return value
    except ValueError:
        raise argparse.ArgumentTypeError("Date must use YYYY-MM-DD format.")


def valid_month(value):
    try:
        datetime.strptime(value, "%Y-%m")
        return value
    except ValueError:
        raise argparse.ArgumentTypeError("Month must use YYYY-MM format.")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Track expenses using a local SQLite database."
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add an expense to the database")
    list_parser = subparsers.add_parser("list", help="List recorded expenses")
    delete_parser = subparsers.add_parser("delete", help="Delete an expense by ID")
    summary_parser = subparsers.add_parser(
        "summary", help="Display total spending and category breakdown"
    )

    add_parser.add_argument("amount", type=positive_amount, help="The amount spent (e.g., 12.50)")
    add_parser.add_argument("category", type=non_empty_string, help="The category (e.g., food)")
    add_parser.add_argument(
        "reason",
        type=str,
        nargs="?",
        default=None,
        help="Optional description for the expense (e.g., lunch)",
    )
    add_parser.add_argument(
        "-d",
        "--date",
        type=valid_date,
        default=None,
        help="Optional date in YYYY-MM-DD format",
    )

    list_parser.add_argument("--category", type=non_empty_string, default=None, help="Filter by category")
    list_parser.add_argument("--month", type=valid_month, default=None, help="Filter by month in YYYY-MM format")

    summary_parser.add_argument("--month", type=valid_month, default=None, help="Filter by month in YYYY-MM format")

    delete_parser.add_argument("id", type=int, help="The ID of the row to delete (e.g., 7)")

    return parser.parse_args()

def format_reason(reason):
    return reason.strip() if reason and reason.strip() else ""


def handle_add(args, conn, cursor):
    reason = format_reason(args.reason)

    if reason:
        print(f"Adding expense: ${args.amount:.2f} for {args.category} ({reason})")
    else:
        print(f"Adding expense: ${args.amount:.2f} for {args.category}")

    cursor.execute(
        "INSERT INTO expenses (amount, category, reason, date) VALUES (?, ?, ?, ?)",
        (args.amount, args.category, reason or None, args.date),
    )

    conn.commit()
    print("Expense recorded successfully.")

def handle_list(args, cursor):
    filters = ["1=1"]
    params = []

    if args.category:
        filters.append("category = ?")
        params.append(args.category)

    if args.month:
        filters.append("date LIKE ?")
        params.append(f"{args.month}%")

    query = (
        "SELECT id, date, category, amount, reason FROM expenses "
        "WHERE " + " AND ".join(filters) + " ORDER BY date DESC, category ASC"
    )

    cursor.execute(query, params)
    rows = cursor.fetchall()

    if not rows:
        print("No expenses found.")
        return
    
    print(f"{'ID':>5} | {'Date':<10} | {'Category':<15} | {'Amount':<11} | {'Reason':<25}")
    print("-" * 72)

    for row in rows:
        row_id, date_value, category, amount, raw_reason = row
        reason = raw_reason or ""
        print(f"{row_id:>5} | {date_value:<10} | {category:<15} | ${amount:<10.2f} | {reason:<25}")

def handle_delete(args, conn, cursor):
    cursor.execute("DELETE FROM expenses WHERE id = ?", (args.id,))
    if cursor.rowcount == 0:
        print(f"No expense found with ID {args.id}.")
    else:
        conn.commit()
        print(f"Deleted expense with ID {args.id}.")

def handle_summary(args, cursor):
    filters = ["1=1"]
    params = []

    if args.month:
        filters.append("date LIKE ?")
        params.append(f"{args.month}%")

    filter_clause = " AND ".join(filters)

    cursor.execute(f"SELECT SUM(amount) FROM expenses WHERE {filter_clause}", params)
    overall_total = cursor.fetchone()[0] or 0

    cursor.execute(
        f"SELECT category, SUM(amount) FROM expenses WHERE {filter_clause} GROUP BY category",
        params,
    )
    breakdown = cursor.fetchall()

    month_text = f" for {args.month}" if args.month else ""
    print(f"Total expenses{month_text}: ${overall_total:.2f}")
    print(f"--- Breakdown by category{month_text} ---")

    for category, total in breakdown:
        print(f"{category.title()}: ${total:.2f}")

def main():
    args = parse_arguments()

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    reason TEXT,
                    date TEXT NOT NULL DEFAULT (DATE('now', 'localtime'))
                )
                """
            )

            if args.command == "add":
                handle_add(args, conn, cursor)
            elif args.command == "list":
                handle_list(args, cursor)
            elif args.command == "delete":
                handle_delete(args, conn, cursor)
            elif args.command == "summary":
                handle_summary(args, cursor)

    except sqlite3.OperationalError as exc:
        print(f"SQLite operational error: {exc}")
    except sqlite3.Error as exc:
        print(f"SQLite error: {exc}")
    except Exception as exc:
        print(f"Unexpected error: {exc}")

if __name__ == "__main__":
    main()