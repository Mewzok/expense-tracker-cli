import sqlite3
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Track expenses by utilizing a local database."
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add an expense to the database")
    list_parser = subparsers.add_parser("list", help="List all recorded expenses in database")

    # required arguments
    add_parser.add_argument("amount", type=float, help="The amount spent(e.g., 12.50)")
    add_parser.add_argument("category", type=str, help="The category (e.g., food)")

    # optional arguments
    add_parser.add_argument("reason", type=str, nargs="?", default=None, help="The description/reason (e.g., lunch) (optional)")

    # optional flag arguments
    add_parser.add_argument("-d", "--date", type=str, default=None, help="Date in YYYY-MM-DD format (optional)")
    list_parser.add_argument("--category", type=str, default=None, help="Filter by category")
    list_parser.add_argument("--month", type=str, default=None, help="Filter by month")

    return parser.parse_args()

def handle_add(args, con, cur):

    print(f"Adding expense: ${args.amount} for {args.category} ({args.reason})")

    if args.date:
        # if user entered date
        cur.execute("""
            INSERT INTO expenses (amount, category, reason, date)
            VALUES (?, ?, ?, ?)
        """, (args.amount, args.category, args.reason, args.date))
    else:
        # if no date provided
        cur.execute("""
            INSERT INTO expenses (amount, category, reason)
            VALUES (?, ?, ?)
        """, (args.amount, args.category, args.reason))

    con.commit()
    print("Expense recorded successfully.")

def handle_list(args, con, cur):

    print("Current Expenses in Database:")

    # dynamically build query to handle arguments

    query = "SELECT date, category, amount, reason FROM expenses WHERE 1=1"
    params = []

    if args.category:
        query += " AND category = ?"
        params.append(args.category)

    if args.month:
        query += " AND date LIKE ?"
        params.append(f"%{args.month}%")

    query += " ORDER BY date DESC, category ASC"

    cur.execute(query, params)
    rows = cur.fetchall()

    con.close()

    print(f"{'Date':<19} | {'Category':<15} | {'Amount':<11} | {'Reason':<25}")
    print("-" * 75)

    for row in rows:
        date, category, amount, raw_reason = row

        # check for reason
        reason = raw_reason or ""

        print(f"{date:<19} | {category:<15} | ${amount:<10.2f} | {reason:<25}")


def main():
    con = None
    args = parse_arguments()

    try:
        # create and/or connect to expenses database
        con = sqlite3.connect("expenses.db")
        cur = con.cursor()

        # create table if doesn't exist yet
        cur.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       amount REAL NOT NULL,
                       category TEXT NOT NULL,
                       reason TEXT,
                       date TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime'))
                    )               
        """)

        if args.command == "add":
            handle_add(args, con, cur)
        elif args.command == "list":
            handle_list(args, con, cur)
        con.close()

    except sqlite3.OperationalError as e:
        print(f"Operational error (e.g., disk full, permissions): {e}")
    except sqlite3.Error as e:
        print(f"General SQLite error: {e}")
    finally:
        if con is not None:
            con.close()

if __name__ == "__main__":
    main()