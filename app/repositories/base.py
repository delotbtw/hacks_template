from collections.abc import Mapping, Sequence
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base


class BaseRepository[ModelT: Base]:
    """Обобщённый CRUD. Наследник задаёт `model`. Коммит делает сервис."""

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, obj_id: int) -> ModelT | None:
        return await self.session.get(self.model, obj_id)

    async def list(self, limit: int = 50, offset: int = 0) -> Sequence[ModelT]:
        stmt = select(self.model).order_by(self.model.id).limit(limit).offset(offset)  # ty: ignore[unresolved-attribute]
        return (await self.session.scalars(stmt)).all()

    async def create(self, data: Mapping[str, Any]) -> ModelT:
        obj = self.model(**data)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, obj: ModelT, data: Mapping[str, Any]) -> ModelT:
        for key, value in data.items():
            setattr(obj, key, value)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj: ModelT) -> None:
        await self.session.delete(obj)
        await self.session.flush()
