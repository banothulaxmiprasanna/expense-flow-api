"""
show_db.py  —  ExpenseFlow POC Database Viewer
================================================
Run this from the expense_flow_api folder:

    python show_db.py

Prints every row in the expenses table as a rich terminal table.
No need to stop the server — run it any time during the demo.
"""

import sqlite3
from rich.console import Console
from rich.table import Table
from rich import box
from rich.panel import Panel
from rich.text import Text

console = Console()


def show_expenses(cur):
    cur.execute("""
        SELECT id, title, amount, currency, expense_date, status,
               submitted_by_id, category_id, description, created_at
        FROM   expenses
        ORDER  BY id
    """)
    rows = cur.fetchall()

    table = Table(
        title="[bold cyan]expenses[/bold cyan]  (SQLite table)",
        box=box.DOUBLE_EDGE,
        header_style="bold white on dark_blue",
        border_style="bright_blue",
        show_lines=True,
    )

    # ── column definitions ────────────────────────────────────
    table.add_column("id",             style="bold yellow",  justify="right",  no_wrap=True)
    table.add_column("title",          style="bright_white", justify="left")
    table.add_column("amount",         style="bold green",   justify="right",  no_wrap=True)
    table.add_column("currency",       style="cyan",         justify="center", no_wrap=True)
    table.add_column("expense_date",   style="magenta",      justify="center", no_wrap=True)
    table.add_column("status",         style="bold",         justify="center", no_wrap=True)
    table.add_column("submitted_by_id",style="dim",          justify="center", no_wrap=True)
    table.add_column("category_id",    style="dim",          justify="center", no_wrap=True)
    table.add_column("description",    style="italic white", justify="left")
    table.add_column("created_at",     style="dim",          justify="left")

    if not rows:
        console.print(table)
        console.print("[yellow]  (empty — no records yet)[/yellow]\n")
        return

    # ── status colour map ─────────────────────────────────────
    status_style = {
        "draft":    "[bold white]draft[/bold white]",
        "pending":  "[bold yellow]pending[/bold yellow]",
        "approved": "[bold green]approved[/bold green]",
        "rejected": "[bold red]rejected[/bold red]",
    }

    for row in rows:
        status_val = str(row["status"]) if row["status"] else "NULL"
        styled_status = status_style.get(status_val, f"[white]{status_val}[/white]")

        table.add_row(
            str(row["id"]),
            str(row["title"]),
            f"{float(row['amount']):.2f}",
            str(row["currency"] or "NULL"),
            str(row["expense_date"] or "NULL"),
            styled_status,
            str(row["submitted_by_id"] or "NULL"),
            str(row["category_id"] or "NULL"),
            str(row["description"] or "—"),
            str(row["created_at"] or "NULL"),
        )

    console.print(table)
    console.print(f"  [bold]Total:[/bold] [green]{len(rows)}[/green] record(s)\n")


# ── Main ──────────────────────────────────────────────────────────────────────
conn = sqlite3.connect("expenseflow.db")
conn.row_factory = sqlite3.Row
cur  = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cur.fetchall()]

console.print()
console.print(Panel(
    Text("ExpenseFlow POC  —  DATABASE VIEWER", style="bold cyan", justify="center"),
    border_style="bright_blue",
))
console.print(f"  [bold]Tables in expenseflow.db:[/bold] [yellow]{', '.join(tables) if tables else '(none)'}[/yellow]\n")

show_expenses(cur)

conn.close()
console.print(Panel(
    Text("End of database snapshot", style="dim", justify="center"),
    border_style="dim",
))
console.print()
