from app.core import config
from app.db import models
from app.db.database import db
from app.schemes import list as list_schema


class ListsRepository:
    async def get_list_url(self, board_id: int, list_id: int):
        return f'{config.BASE_URL}{config.API_PREFIX}/boards/{board_id}/lists/{list_id}'

    async def get_list_by_id(self, list_id: int):
        return await models.List.get(list_id)

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


list_repo = ListsRepository()
