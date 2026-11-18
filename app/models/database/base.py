# models/database/base.py
#
# The foundation that every database model (table class) is built on top of.
#
# TWO THINGS DEFINED HERE:
#   1. Base           — the parent class for ALL database models.
#                       SQLAlchemy uses it to track every table.
#   2. TimestampMixin — adds created_at + updated_at columns
#                       to any model that inherits it.
#                       Write it ONCE here, reuse everywhere.
#
# WHY SEPARATE FILES?
#   If we defined Base inside expense.py, and user.py also
#   imported it, we'd have two different Base objects — and
#   SQLAlchemy would only know about one set of tables.
#   One Base = one source of truth for the whole database.

from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# ─────────────────────────────────────────────────────────────
# Base — the parent of every database model
#
# `DeclarativeBase` is a SQLAlchemy 2.x class. When you inherit
# from `Base` in your model, SQLAlchemy automatically registers
# that model's `__tablename__` and columns in its metadata.
#
# `Base.metadata` is a registry. It knows every table.
# When we call `Base.metadata.create_all(engine)`, SQLAlchemy
# generates and runs the CREATE TABLE SQL for every registered
# model that hasn't been created yet.
# ─────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ─────────────────────────────────────────────────────────────
# TimestampMixin — reusable audit columns
#
# A "mixin" is a class that is NOT used on its own.
# It only exists to be inherited by real classes, adding
# extra columns to them.
#
# Every table in a real application needs:
#   - created_at: when was this record first created?
#   - updated_at: when was this record last changed?
#
# Without a mixin:
#   You'd write the same two columns in expense.py, user.py,
#   category.py, department.py... over and over.
#
# With a mixin:
#   Write once here.
#   class Expense(Base, TimestampMixin):  ← done. Both columns added.
#
# func.now() is a SQLAlchemy helper that calls the database's
# built-in NOW() function — so timestamps use DB server time,
# not the Python server's clock.
# ─────────────────────────────────────────────────────────────
class TimestampMixin:
    """Adds created_at and updated_at audit columns to any model."""

    created_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        onupdate=func.now(),
    )
