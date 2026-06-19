import sqlite3
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Track expenses by utilizing a local database."
    )

    parser.add_argument("add", action="store_true", help="Add expense to database")

def main():
    con = None

    # testing
    expense_data = (14.99, "bills", "netflix subscription")

    try:
        # create and/or connect to expenses database
        con = sqlite3.connect("expenses.db")
        cursor = con.cursor()

        con.execute("DROP TABLE expenses")

        # create table if doesn't exist yet
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       amount REAL NOT NULL,
                       category TEXT NOT NULL,
                       reason TEXT,
                       date TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime'))
                    )               
        """)

        cursor.execute("""
            INSERT INTO expenses (amount, category, reason)
            VALUES (?, ?, ?)
        """, expense_data)

        con.commit()

        print("Current Expenses in Database:")
        for row in cursor.execute("SELECT amount, category, reason, date FROM expenses ORDER BY date"):
            print(row)

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