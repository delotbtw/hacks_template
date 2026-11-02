from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import ItemServiceDep
from app.core.errors import ErrorResponse
from app.schemas.item import ItemCreate, ItemRead, ItemUpdate

router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)


@router.get("", response_model=list[ItemRead])
async def list_items(
    service: ItemServiceDep,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return await service.list(limit, offset)


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(data: ItemCreate, service: ItemServiceDep):
    return await service.create(data)


@router.get("/{item_id}", response_model=ItemRead)
async def get_item(item_id: int, service: ItemServiceDep):
    return await service.get(item_id)


@router.patch("/{item_id}", response_model=ItemRead)
async def update_item(item_id: int, data: ItemUpdate, service: ItemServiceDep):
    return await service.update(item_id, data)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, service: ItemServiceDep) -> None:
    await service.delete(item_id)
