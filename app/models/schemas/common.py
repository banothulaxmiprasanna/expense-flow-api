# ============================================================
# SESSION 3 — FILE 3 OF 4: common.py
# ============================================================
# WHAT THIS FILE IS:
#   Shared/reusable schemas used across multiple endpoints.
#   Not tied to one entity — used by expenses, users, categories.
#
# KEY THINGS TO POINT OUT DURING SESSION:
#   - PaginationParams: Pydantic works for QUERY PARAMS too
#     (not just request body — used with Depends() in routes)
#   - PaginatedResponse[T]: Generic schema — T is a placeholder
#     PaginatedResponse[ExpenseResponse] → items: list[ExpenseResponse]
#     PaginatedResponse[UserResponse]    → items: list[UserResponse]
#     One class, works for any entity. Write once, use everywhere.
#   - ErrorResponse: consistent error shape across all endpoints
# ============================================================

from typing import Generic, TypeVar
from pydantic import BaseModel, Field

# T is a "type variable" — a blank placeholder.
# When you use PaginatedResponse[ExpenseResponse], T = ExpenseResponse.
T = TypeVar("T")


# ─────────────────────────────────────────────────────────────
# PaginationParams — used as query parameters, not request body
# In a route: def list_expenses(paging: PaginationParams = Depends())
# FastAPI reads ?page=2&per_page=10 from the URL and validates here.
# ─────────────────────────────────────────────────────────────
class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number (starts from 1)")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page (max 100)")

    @property
    def skip(self) -> int:
        """How many records to skip in the database query."""
        return (self.page - 1) * self.per_page


# ─────────────────────────────────────────────────────────────
# PaginatedResponse[T] — generic wrapper for list responses
# Instead of returning a flat array, we wrap with pagination info.
# Usage:
#   PaginatedResponse[ExpenseResponse]   →  items = list[ExpenseResponse]
#   PaginatedResponse[UserResponse]      →  items = list[UserResponse]
# ─────────────────────────────────────────────────────────────
class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int = Field(..., description="Total number of matching records in the database")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of items per page")
    has_next: bool = Field(..., description="True if there are more pages after this one")


# ─────────────────────────────────────────────────────────────
# ErrorResponse — consistent error shape across all endpoints
# All AppExceptions return this structure so clients always
# know where to find the error message.
# ─────────────────────────────────────────────────────────────
class ErrorResponse(BaseModel):
    error_code: str = Field(..., description="Machine-readable error code e.g. EXPENSE_NOT_FOUND")
    detail: str = Field(..., description="Human-readable error message")
    context: dict | None = Field(default=None, description="Optional extra details about the error")
