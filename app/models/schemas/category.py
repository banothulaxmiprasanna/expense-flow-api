# ============================================================
# SESSION 3 — FILE 4 OF 4: category.py
# ============================================================
# WHAT THIS FILE IS:
#   Pydantic schemas for the Category entity.
#   This is the SIMPLEST example — a good starting point.
#   No validators, no complex inheritance.
#   Just: Base + Response with from_attributes.
#
# KEY THINGS TO POINT OUT DURING SESSION:
#   - CategoryBase: no Field() rules on most fields — type hints alone
#   - max_amount: a float with no gt/ge — only type enforced here
#   - CategoryResponse: adds just `id` — simplest inheritance example
#   - ConfigDict: alternative way to write model_config (same result)
# ============================================================

from pydantic import BaseModel, ConfigDict


# ─────────────────────────────────────────────────────────────
# CategoryBase — base fields for a category
# ─────────────────────────────────────────────────────────────
class CategoryBase(BaseModel):
    name: str
    description: str | None = None
    requires_receipt: bool = True          # default True — most categories need a receipt
    max_amount: float                      # max allowed expense amount in this category


# ─────────────────────────────────────────────────────────────
# CategoryResponse — what the API returns for a category
# Note: ConfigDict is the same as model_config = {"from_attributes": True}
#       — just written using the ConfigDict helper class
# ─────────────────────────────────────────────────────────────
class CategoryResponse(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
