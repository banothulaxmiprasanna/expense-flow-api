# app/repositories/base.py
# BaseRepository — generic CRUD operations for any SQLAlchemy model

from typing import Generic, TypeVar, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database.base import Base

# TypeVar ties the generic to classes that inherit from Base
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic repository that provides create / get_by_id / get_all / delete
    for any SQLAlchemy model that inherits from Base.

    Usage:
        repo = ExpenseRepository(session=db)
        expense = await repo.get_by_id(1)
    """

    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, data: dict[str, Any]) -> ModelType:
        """Create a new row and return the saved object (with id and timestamps)."""
        db_obj = self.model(**data)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def get_by_id(self, id: int) -> ModelType | None:
        """Return the row with this id, or None if not found."""
        return await self.session.get(self.model, id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Return up to `limit` rows starting from `skip`."""
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, id: int) -> bool:
        """Delete the row with this id. Returns True if deleted, False if not found."""
        obj = await self.get_by_id(id)
        if obj is None:
            return False
        await self.session.delete(obj)
        await self.session.commit()
        return True
