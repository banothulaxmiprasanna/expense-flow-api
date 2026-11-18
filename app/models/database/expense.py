# models/database/expense.py
#
# SQLAlchemy database model for the Expense table.
# This class IS the `expenses` table in the database.
# Each instance of this class = one row in that table.
#
# NOTE — two expense files serve different purposes:
#   schemas/expense.py  → Pydantic: validates data coming IN via API
#   database/expense.py → SQLAlchemy: maps Python class to DB table
#
#   Pydantic Schema  ──► Service Layer ──► DB Model ──► Database

from datetime import date, datetime
from sqlalchemy import Text, Float, String, Date
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin


class Expense(Base, TimestampMixin):
    """Database model for the expenses table."""

    # ─────────────────────────────────────────────────────────
    # __tablename__
    # Tells SQLAlchemy: create a table with this name in the DB.
    # Convention: plural, lowercase, underscores.
    # Python class = singular (Expense)
    # DB table     = plural  (expenses)
    # ─────────────────────────────────────────────────────────
    __tablename__ = "expenses"

    # ─────────────────────────────────────────────────────────
    # PRIMARY KEY
    # Every table must have a primary key — a unique ID for
    # each row. `int` type means SQLAlchemy uses auto-increment.
    # SQLite creates each expense with id=1, id=2, id=3...
    # ─────────────────────────────────────────────────────────
    id: Mapped[int] = mapped_column(primary_key=True)

    # ─────────────────────────────────────────────────────────
    # CORE FIELDS
    #
    # Mapped[str]   → this column stores text, is REQUIRED
    # Mapped[float] → this column stores a decimal number
    # Mapped[date]  → stores a calendar date (no time)
    #
    # String(100)   → VARCHAR(100) in SQL — max 100 characters
    # index=True    → creates a DB index on this column,
    #                 making searches on title/status faster
    # ─────────────────────────────────────────────────────────
    title: Mapped[str] = mapped_column(String(100), index=True)
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    expense_date: Mapped[date] = mapped_column(Date)

    # ─────────────────────────────────────────────────────────
    # OPTIONAL FIELDS
    #
    # Mapped[str | None] → column can be NULL in the database
    # `| None` is the Python 3.10+ way to say "optional"
    # Text → for long text with no length limit (vs String(100))
    # ─────────────────────────────────────────────────────────
    description: Mapped[str | None] = mapped_column(Text)
    receipt_url: Mapped[str | None]

    # ─────────────────────────────────────────────────────────
    # STATUS FIELD — the workflow state machine
    #
    # An expense travels through these states:
    #   draft → submitted → approved OR rejected
    #
    # default="draft" means every new expense starts as draft.
    # index=True because we will frequently filter by status:
    #   "show me all submitted expenses waiting for review"
    # ─────────────────────────────────────────────────────────
    status: Mapped[str] = mapped_column(default="draft", index=True)

    # ─────────────────────────────────────────────────────────
    # MANAGER COMMENT
    #
    # When a manager approves or rejects an expense, they can
    # leave a comment explaining their decision.
    # NULL until the expense is reviewed.
    # ─────────────────────────────────────────────────────────
    manager_comment: Mapped[str | None] = mapped_column(Text)

    # ─────────────────────────────────────────────────────────
    # WORKFLOW TIMESTAMPS
    #
    # These are separate from created_at / updated_at.
    # They track exactly WHEN each workflow transition happened:
    #   submitted_at → when did the employee click "submit"?
    #   reviewed_at  → when did the manager approve/reject?
    #
    # All start as None (NULL) and are set only when the
    # corresponding action actually happens.
    # ─────────────────────────────────────────────────────────
    submitted_at: Mapped[datetime | None]
    reviewed_at: Mapped[datetime | None]

    # ─────────────────────────────────────────────────────────
    # FOREIGN KEY COLUMNS
    #
    # A ForeignKey is a column whose value MUST exist in
    # another table's primary key column.
    #
    # category_id = 3 means: this expense belongs to the
    #   category whose id=3 in the categories table.
    #
    # submitted_by_id = 7 means: this expense was submitted
    #   by the user whose id=7 in the users table.
    #
    # reviewed_by_id → None until a manager reviews it.
    #
    # NOTE: We are storing just the IDs here as plain integers.
    # ForeignKey constraints will be added in a later session once
    # we also create the Category and User database models.
    # In that session we will also add `relationship()` to let
    # Python automatically load the full Category/User objects.
    # ─────────────────────────────────────────────────────────
    category_id: Mapped[int]
    submitted_by_id: Mapped[int]
    reviewed_by_id: Mapped[int | None]
