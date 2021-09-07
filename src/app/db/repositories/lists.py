from fastapi import HTTPException
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_400_BAD_REQUEST,
)


from app.core import config
from app.db import models
from app.db.database import db
from app.schemes import list as list_schema


class ListsRepository:
    async def get_list_url(self, board_id: int, list_id: int):
        return f'{config.BASE_URL}{config.API_PREFIX}/boards/{board_id}/lists/{list_id}'

    async def get_cards_url(self, board_id: int, list_id: int):
        return f'{config.BASE_URL}{config.API_PREFIX}/boards/{board_id}/lists/{list_id}/cards'

    async def get_list_by_id(self, list_id: int):
        return await models.List.get(list_id)

    async def get_list_by_id_and_check_board_foreign_key(self, *, list_id: int, board: models.Board):
        lst = await models.List.get(list_id)

        if not lst:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f"List ({list_id}) not found."
            )

        if lst.board_id != board.id:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f"List ({list_id}) not found."
            )
            # raise HTTPException(
            #     status_code=HTTP_400_BAD_REQUEST,
            #     detail=f"List ({lst.id}) does not connected to Board ({board.id})"
            # )

        return lst

    async def create_new_list(self, *, list_obj: list_schema.ListCreate, created_by: models.User):
        return await models.List.create(**list_obj.dict(), **{'created_by_id': created_by.id})

    async def get_multiple_lists(self, *, board_id: int, offset=0, limit=25):
        if not limit:
            limit = 25

        async with db.transaction():
            cursor = await models.List.query.where(models.List.board_id == board_id).gino.iterate()
            if offset:
                await cursor.forward(offset)
            lists = await cursor.many(limit)
        return lists

    async def update(self, *, lst: models.List, updated_list: list_schema.ListUpdate):
        print(updated_list.dict())
        await lst.update(**updated_list.dict()).apply()


list_repo = ListsRepository()