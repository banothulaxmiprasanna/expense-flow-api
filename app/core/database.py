# core/database.py
#
# The single place where the database connection is set up.
# Every other file that needs the database imports from here.
#
# THREE THINGS THIS FILE CREATES:
#   1. engine       — the actual connection to the database file
#   2. SessionLocal — a factory that creates database sessions
#   3. get_db       — a FastAPI dependency that hands a session
#                     to any route that asks for it, and closes
#                     it automatically when the request ends
#
# WHY ASYNC?
#   Our API handles multiple requests at the same time.
#   Async means: while waiting for a slow DB query, Python can
#   serve another incoming request instead of just sitting idle.
#   `aiosqlite` makes SQLite work in async mode.

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from app.core.config import get_settings

# ─────────────────────────────────────────────────────────────
# STEP 1 — Read settings (DATABASE_URL comes from .env)
# ─────────────────────────────────────────────────────────────
settings = get_settings()

# ─────────────────────────────────────────────────────────────
# STEP 2 — Create the engine
#
# The engine is the low-level object that manages the actual
# connection pool to the database file.
#
# DATABASE_URL format for SQLite async:
#   sqlite+aiosqlite:///./expenseflow.db
#   │       │          │   └─ filename (relative path)
#   │       │          └─ three slashes = relative path
#   │       └─ aiosqlite driver (async SQLite)
#   └─ database type
#
# echo=settings.DEBUG means: when DEBUG=True, SQLAlchemy will
# print every SQL statement it runs into the terminal.
# Very useful while learning — you can see exactly what SQL
# your Python code generates.
# ─────────────────────────────────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)

# ─────────────────────────────────────────────────────────────
# STEP 3 — Create the session factory
#
# `async_sessionmaker` is a factory (a machine that produces
# sessions). Calling SessionLocal() gives you one fresh session.
#
# autocommit=False  → changes are NOT saved unless we say so
# autoflush=False   → don't auto-send pending changes to DB
# expire_on_commit  → after commit, keep objects usable in Python
# ─────────────────────────────────────────────────────────────
SessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# ─────────────────────────────────────────────────────────────
# STEP 4 — The dependency function
#
# `get_db` is a FastAPI dependency.
# When a route declares `db: AsyncSession = Depends(get_db)`,
# FastAPI calls this function, gives the route the `session`,
# and when the route finishes (success or error), the
# `async with` block closes the session automatically.
#
# `yield` is the keyword that splits "before request" (open
# the session) from "after request" (close the session).
# ─────────────────────────────────────────────────────────────
async def get_db() -> AsyncSession:
    """FastAPI dependency — provides a database session per request."""
    async with SessionLocal() as session:
        yield session
