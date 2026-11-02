from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.models.item import Item
from app.repositories.item import ItemRepository
from app.schemas.item import ItemCreate, ItemUpdate


class ItemService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = ItemRepository(session)

    async def list(self, limit: int, offset: int) -> Sequence[Item]:
        return await self.repo.list(limit=limit, offset=offset)

    async def get(self, item_id: int) -> Item:
        item = await self.repo.get(item_id)
        if item is None:
            raise NotFoundError("Item")
        return item

    async def create(self, data: ItemCreate) -> Item:
        item = await self.repo.create(data.model_dump())
        await self.session.commit()
        return item

    async def update(self, item_id: int, data: ItemUpdate) -> Item:
        item = await self.get(item_id)
        item = await self.repo.update(item, data.model_dump(exclude_unset=True))
        await self.session.commit()
        return item

    async def delete(self, item_id: int) -> None:
        item = await self.get(item_id)
        await self.repo.delete(item)
        await self.session.commit()
