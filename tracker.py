import sqlite3
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Track expenses by utilizing a local database."
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add an expense to the database")

    # required arguments
    add_parser.add_argument("amount", type=float, help="The amount spent(e.g., 12.50)")
    add_parser.add_argument("category", type=str, help="The category (e.g., food)")

    # optional arguments
    add_parser.add_argument("reason", type=str, nargs="?", default=None, help="The description/reason (e.g., lunch) (optional)")

    # optional flag arguments
    add_parser.add_argument("-d", "--date", type=str, default=None, help="Date in YYYY-MM-DD format (optional)")

    return parser.parse_args()

def handle_add(args, con, cur):
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


def main():
    con = None
    args = parse_arguments()

    print(f"Adding expense: ${args.amount} for {args.category} ({args.reason})")

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

        handle_add(args, con, cur)

        print("Current Expenses in Database:")
        for row in cur.execute("SELECT amount, category, reason, date FROM expenses ORDER BY date"):
            amount, category, reason, date = row
            display_reason = reason if reason is not None else ""
            print(f"{date} | {category} | ${amount:<7.2f} | {display_reason}")

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