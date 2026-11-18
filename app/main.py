
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import engine, get_db

# Base must be imported so SQLAlchemy knows about all models when create_all runs
from app.models.database.base import Base
from app.models.database.expense import Expense  # noqa: F401 — registers the table

from app.models.schemas.expense import ExpenseCreate, ExpenseReviewAction
from app.models.schemas.user import UserCreate

from app.repositories.expense_repo import ExpenseRepository

settings = get_settings()


# ─────────────────────────────────────────────────────────────
# get_expense_repo — dependency that creates ExpenseRepository
# FastAPI calls this automatically for any route that declares:
#   repo: ExpenseRepository = Depends(get_expense_repo)
# ─────────────────────────────────────────────────────────────
async def get_expense_repo(db: AsyncSession = Depends(get_db)) -> ExpenseRepository:
    return ExpenseRepository(session=db)


# ─────────────────────────────────────────────────────────────
# lifespan — runs on server startup and shutdown
#
# BEFORE yield → startup: create all DB tables that don't exist yet
# AFTER  yield → shutdown: dispose connection pool cleanly
#
# engine.begin() opens a single connection for DDL work.
# conn.run_sync(Base.metadata.create_all) generates and runs
# CREATE TABLE IF NOT EXISTS for every registered model.
# ─────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── STARTUP ──
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield  # server runs and accepts requests here

    # ── SHUTDOWN ──
    await engine.dispose()


app = FastAPI(
    title="ExpenseFlow API",
    description="""
## ExpenseFlow API

Smart Employee Expense Reimbursement System.

### Database demo endpoints:
- **GET /demo/db-check** — confirms DB is connected and lists all tables created
- **POST /demo/db-save** — saves a real expense row and returns the saved data

### Schema validation demo endpoints:
- **POST /demo/expense** — validates expense data via Pydantic schema
- **POST /demo/user** — validates user registration data via Pydantic schema
- **POST /demo/review** — validates approve/reject action via Literal type
    """,
    version="0.4.0",
    lifespan=lifespan,
)




@app.get("/", tags=["Health"])
def root():
    return {
        "message": "ExpenseFlow API is running",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
    }


@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "ok",
        "version": "0.4.0",
    }



@app.post("/demo/expense", tags=["Schema Validation Demo"])
def demo_create_expense(expense: ExpenseCreate):
    """
    **ExpenseCreate Schema — Pydantic validation**

    Paste this in the request body to test VALID data:
    ```json
    {
      "title": "Team Lunch",
      "amount": 250.00,
      "currency": "USD",
      "expense_date": "2026-04-10",
      "category_id": 1
    }
    ```

    Now try INVALID data and watch Pydantic block it:
    - `amount: -100`  → blocked (must be > 0)
    - `title: "Hi"`   → blocked (min_length is 3)
    - `expense_date: "2030-01-01"` → blocked (cannot be in the future)
    - `category_id: 0` → blocked (must be >= 1)
    """
    return {
        "message": "Pydantic validation passed! Data accepted.",
        "received": expense.model_dump(),
        "note": "In the real app this would be saved to the database via Service → Repository layers."
    }


@app.post("/demo/user", tags=["Schema Validation Demo"])
def demo_create_user(user: UserCreate):
    """
    **UserCreate Schema — Pydantic validation**

    Paste this to test VALID data:
    ```json
    {
      "email": "ravi.kumar@company.com",
      "full_name": "Ravi Kumar",
      "employee_id": "EMP-1234",
      "password": "SecurePass1",
      "department_id": 2
    }
    ```

    Now try INVALID data:
    - `email: "not-an-email"` → blocked (invalid email format)
    - `employee_id: "EMP-12"` → blocked (pattern requires 4-6 digits)
    - `employee_id: "1234"` → blocked (must start with EMP-)
    - `password: "password"` → blocked (no uppercase letter)
    - `password: "Password"` → blocked (no number)
    """
    return {
        "message": "Pydantic validation passed! User data accepted.",
        "received": {
            "email": user.email,
            "full_name": user.full_name,
            "employee_id": user.employee_id,
            "role": user.role,
            "department_id": user.department_id,
            # NOTE: never echo passwords back — even in a demo
            "password": "***hidden***",
        },
        "note": "In the real app the password would be hashed via bcrypt before being saved."
    }


@app.post("/demo/review", tags=["Schema Validation Demo"])
def demo_review_action(action: ExpenseReviewAction):
    """
    **ExpenseReviewAction Schema — Literal type validation**

    Paste this to test VALID data:
    ```json
    {
      "action": "approve",
      "comment": "Looks good, approved for reimbursement."
    }
    ```

    Now try INVALID data:
    - `action: "accepted"` → blocked (Literal only allows 'approve' or 'reject')
    - `comment: "OK"` → blocked (min_length is 10 characters)
    """
    return {
        "message": f"Review action '{action.action}' accepted by Pydantic.",
        "received": action.model_dump(),
        "note": "The Literal type restricts action to ONLY 'approve' or 'reject' — nothing else."
    }


@app.get("/demo/db-check", tags=["Database Demo"])
async def demo_db_check(db: AsyncSession = Depends(get_db)):
    """
    **DB Check — confirms the database is connected**

    This endpoint asks the database: "what tables exist?"
    SQLite keeps a list of all tables in a special internal
    table called `sqlite_master`.

    Hit **Execute** — you will see the `expenses` table listed.
    That table was created automatically by SQLAlchemy when the
    server started, from the `Expense` class in our Python code.

    No SQL was written manually. SQLAlchemy generated it.
    """
    # Run raw SQL: ask SQLite for all table names
    result = await db.execute(
        text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    )
    tables = [row[0] for row in result.fetchall()]

    return {
        "message": "Database is connected!",
        "tables_created_by_sqlalchemy": tables,
        "how": "SQLAlchemy read our Expense class and ran CREATE TABLE automatically on startup.",
        "db_file": "Look in your project folder — you will see expenseflow.db was created on disk.",
    }


@app.post("/demo/db-save", tags=["Database Demo"])
async def demo_db_save(expense: ExpenseCreate, db: AsyncSession = Depends(get_db)):
    """
    **DB Save — saves a real expense row to the database**

    This endpoint takes a validated expense (Pydantic schema)
    and saves it as a real row in the database.

    Paste this in the request body:
    ```json
    {
      "title": "Team Lunch",
      "amount": 250.00,
      "currency": "USD",
      "expense_date": "2026-04-14",
      "category_id": 1
    }
    ```

    Watch the terminal — because DEBUG=True, SQLAlchemy prints
    the exact INSERT SQL it ran. Hit this endpoint multiple
    times — each row gets a new auto-incremented `id`.

    Then hit **GET /demo/db-check** again to confirm the table
    is still there with all your rows.
    """
    # Create a database model instance from the validated schema data
    db_expense = Expense(
        title=expense.title,
        amount=expense.amount,
        currency=expense.currency,
        expense_date=expense.expense_date,
        description=expense.description,
        receipt_url=expense.receipt_url,
        category_id=expense.category_id,
        # For the demo we hard-code submitted_by_id = 1
        # In the real app this comes from the logged-in user's token
        submitted_by_id=1,
        status="draft",
    )

    db.add(db_expense)          # stage the INSERT (SQL not run yet)
    await db.commit()           # run the INSERT → row appears in DB
    await db.refresh(db_expense)  # reload from DB to get auto-assigned id

    return {
        "message": "Expense saved to the database!",
        "saved_row": {
            "id": db_expense.id,
            "title": db_expense.title,
            "amount": db_expense.amount,
            "currency": db_expense.currency,
            "expense_date": str(db_expense.expense_date),
            "status": db_expense.status,
            "category_id": db_expense.category_id,
            "created_at": str(db_expense.created_at),
        },
        "note": (
            "id was auto-assigned by SQLite. "
            "created_at was set by the TimestampMixin. "
            "Check the terminal — you saw the INSERT SQL SQLAlchemy generated."
        ),
    }


# ═════════════════════════════════════════════════════════════
# SESSION 5 — Repository Pattern Demo
# ═════════════════════════════════════════════════════════════

@app.get("/demo/repo-list", tags=["Repository Pattern Demo"])
async def demo_repo_list(repo: ExpenseRepository = Depends(get_expense_repo)):
    """
    **Repository Pattern Demo — List all expenses**

    Uses `ExpenseRepository.get_all()` to fetch all rows.
    The route has ZERO SQLAlchemy code — all DB logic is in the repository.

    Compare this to `POST /demo/db-save` which had `db.add / commit / refresh`
    directly in the route. Here the route just calls one method.
    """
    expenses = await repo.get_all()
    return {
        "message": f"Found {len(expenses)} expense(s) in the database.",
        "expenses": [
            {
                "id": e.id,
                "title": e.title,
                "amount": e.amount,
                "status": e.status,
                "created_at": str(e.created_at),
            }
            for e in expenses
        ],
        "note": "This data came from ExpenseRepository.get_all() — no SQL in this route.",
    }


@app.get("/demo/repo-get/{id}", tags=["Repository Pattern Demo"])
async def demo_repo_get(id: int, repo: ExpenseRepository = Depends(get_expense_repo)):
    """
    **Repository Pattern Demo — Get one expense by ID**

    Uses `ExpenseRepository.get_by_id(id)`.
    Returns 404 if the id does not exist in the database.

    Try with id=1 (should succeed), then try id=9999 (should return 404).
    """
    from fastapi import HTTPException
    expense = await repo.get_by_id(id)
    if expense is None:
        raise HTTPException(status_code=404, detail=f"Expense with id={id} not found.")
    return {
        "message": f"Expense id={id} found.",
        "expense": {
            "id": expense.id,
            "title": expense.title,
            "amount": expense.amount,
            "currency": expense.currency,
            "status": expense.status,
            "created_at": str(expense.created_at),
        },
    }


@app.delete("/demo/repo-delete/{id}", tags=["Repository Pattern Demo"])
async def demo_repo_delete(id: int, repo: ExpenseRepository = Depends(get_expense_repo)):
    """
    **Repository Pattern Demo — Delete one expense by ID**

    Uses `ExpenseRepository.delete(id)`.
    Returns 404 if the id does not exist.

    After deleting, run `GET /demo/repo-list` to confirm the row is gone.
    Try deleting the same id again — you will get 404.
    """
    from fastapi import HTTPException
    deleted = await repo.delete(id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Expense with id={id} not found.")
    return {
        "message": f"Expense id={id} deleted successfully.",
        "note": "Run GET /demo/repo-list to confirm the row is gone.",
    }
