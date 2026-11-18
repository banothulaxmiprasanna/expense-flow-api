# ============================================================
# SESSION 3 — FILE 1 OF 4: expense.py
# ============================================================
# WHAT THIS FILE IS:
#   The Pydantic schema definitions for the Expense entity.
#   Every request body for expense endpoints is validated here.
#   Every response shape is defined here.
#
# WHAT FRESHERS BUILD HERE:
#   Step 1 — ExpenseBase    (shared fields, written once)
#   Step 2 — ExpenseCreate  (inherits Base + date validator)
#   Step 3 — ExpenseUpdate  (all fields optional — for PATCH)
#   Step 4 — ExpenseReviewAction  (approve/reject endpoint)
#   Step 5 — ExpenseResponse (inherits Base + DB fields)
# ============================================================

from typing import Literal
from datetime import date
from pydantic import BaseModel, Field, model_validator


# ─────────────────────────────────────────────────────────────
# STEP 1: ExpenseBase — shared fields with all rules
# Both ExpenseCreate and ExpenseResponse inherit from this.
# Change a rule here → ALL child classes get it automatically.
# ─────────────────────────────────────────────────────────────
class ExpenseBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Short title for the expense")
    amount: float = Field(..., gt=0, description="Must be a positive number")
    currency: str = Field(default="USD", min_length=3, max_length=3, description="3-letter currency code")
    expense_date: date = Field(..., description="Date when the expense occurred (YYYY-MM-DD)")
    description: str | None = Field(default=None, description="Optional longer description")
    receipt_url: str | None = Field(default=None, description="Optional URL to uploaded receipt")
    category_id: int = Field(..., ge=1, description="ID of the expense category")


# ─────────────────────────────────────────────────────────────
# STEP 2: ExpenseCreate — used for POST /expenses
# Inherits all fields from ExpenseBase.
# Adds a @model_validator that checks the date is not in the
# future and not older than 90 days (needs the whole object).
# ─────────────────────────────────────────────────────────────
class ExpenseCreate(ExpenseBase):

    @model_validator(mode='after')
    def validate_date(self) -> 'ExpenseCreate':
        today = date.today()
        if self.expense_date > today:
            raise ValueError("Expense date cannot be in the future")
        if (today - self.expense_date).days > 90:
            raise ValueError("Expense date must be within the last 90 days")
        return self


# ─────────────────────────────────────────────────────────────
# STEP 3: ExpenseUpdate — used for PATCH /expenses/{id}
# Does NOT inherit from ExpenseBase.
# WHY: ExpenseBase has required fields (title, amount, etc.).
#      A PATCH request should allow sending ONLY the fields
#      you want to change — everything else stays as-is.
#      So every field here is optional: str | None = None
# ─────────────────────────────────────────────────────────────
class ExpenseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=100)
    amount: float | None = Field(default=None, gt=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    expense_date: date | None = None
    description: str | None = None
    receipt_url: str | None = None
    category_id: int | None = None


# ─────────────────────────────────────────────────────────────
# STEP 4: ExpenseReviewAction — used for POST /expenses/{id}/review
# Standalone schema — does NOT inherit from ExpenseBase.
# Only used by the approve/reject endpoint.
# Literal["approve", "reject"] means ONLY those two strings allowed.
# ─────────────────────────────────────────────────────────────
class ExpenseReviewAction(BaseModel):
    action: Literal["approve", "reject"] = Field(..., description="Must be 'approve' or 'reject'")
    comment: str = Field(..., min_length=10, description="Manager's comment (min 10 characters)")


# ─────────────────────────────────────────────────────────────
# STEP 5: ExpenseResponse — used as the return shape for GET/POST
# Inherits all fields from ExpenseBase.
# Adds database-generated fields: id, status, submitted_by_id, etc.
# model_config from_attributes=True: because SQLAlchemy gives us
#   Python OBJECTS (row.id, row.title) — not dicts.
#   Without this setting, Pydantic cannot read from objects.
# ─────────────────────────────────────────────────────────────
class ExpenseResponse(ExpenseBase):
    id: int
    status: str
    submitted_by_id: int
    reviewed_by_id: int | None = None
    manager_comment: str | None = None
    payment_reference: str | None = None

    model_config = {"from_attributes": True}
