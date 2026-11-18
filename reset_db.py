"""
reset_db.py  —  ExpenseFlow POC Database Reset
================================================
Run this from the expense_flow_api folder:

    python reset_db.py

What it does:
  - Deletes ALL rows from the expenses table
  - Resets the auto-increment counter so next id starts at 1 again
  - Does NOT drop or delete the database file
  - Does NOT require restarting the API server

Use this before a demo to start with a clean slate.
"""

import sqlite3


def reset_database():
    print("\n" + "=" * 60)
    print("  ExpenseFlow POC  —  DATABASE RESET")
    print("=" * 60)

    conn = sqlite3.connect("expenseflow.db")
    cur  = conn.cursor()

    # Check how many rows exist before reset
    cur.execute("SELECT COUNT(*) FROM expenses")
    count_before = cur.fetchone()[0]
    print(f"\n  Rows in expenses before reset : {count_before}")

    # Delete all rows from expenses
    cur.execute("DELETE FROM expenses")

    # Reset the auto-increment counter so next id = 1
    # sqlite_sequence only exists after the first autoincrement insert, so check first
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence'")
    if cur.fetchone():
        cur.execute("DELETE FROM sqlite_sequence WHERE name='expenses'")

    conn.commit()

    # Verify
    cur.execute("SELECT COUNT(*) FROM expenses")
    count_after = cur.fetchone()[0]
    print(f"  Rows in expenses after  reset : {count_after}")

    conn.close()

    print("\n  Done! Database is clean.")
    print("  Next expense you create will get id = 1")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    confirm = input("  This will delete ALL expense rows. Type 'yes' to confirm: ").strip().lower()
    if confirm == "yes":
        reset_database()
    else:
        print("\n  Reset cancelled. No data was changed.\n")
