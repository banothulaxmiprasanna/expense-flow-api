# app/repositories/expense_repo.py
# ExpenseRepository — expense-specific DB operations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.repositories.base import BaseRepository
from app.models.database.expense import Expense


class ExpenseRepository(BaseRepository[Expense]):
    """
    Repository for the Expense model.
    Inherits: create / get_by_id / get_all / delete from BaseRepository.
    Adds: get_by_status — filter expenses by their status field.
    """

    def __init__(self, session: AsyncSession):
        # Pass the Expense model class and session to the base class
        super().__init__(model=Expense, session=session)

    async def get_by_status(self, status: str) -> list[Expense]:
        """Return all expenses with the given status (draft / pending / approved / rejected)."""
        stmt = select(Expense).where(Expense.status == status)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
