from app.core import config
from app.db import models
from app.db.database import db
from app.schemes import board as board_schema
from app.services import auth_service


class BoardsRepository:
    def __init__(self):
        self.auth_service = auth_service

    async def get_board_url(self, board_id: int):
        return f'{config.BASE_URL}{config.API_PREFIX}/boards/{board_id}'

    async def get_board(self, board_id: int):
        return await models.Board.get(board_id)

    async def create_new_board(self, *, board: board_schema.BoardCreate, owner: models.User):
        return await models.Board.create(**board.dict(), **{'owner_id': owner.id})

    async def get_all_public_boards(self, *, offset=0, limit=25):
        if not limit:
            limit = 25

        async with db.transaction():
            cursor = await models.Board.query.where(models.Board.public == True).gino.iterate()
            if offset:
                await cursor.forward(offset)
            boards = await cursor.many(limit)
        return boards

    async def get_my_boards(self, *, user: models.User, offset=0, limit=25):
        if not limit:
            limit = 25

        async with db.transaction():
            cursor = await models.Board.query.where(models.Board.owner_id == user.id).gino.iterate()
            if offset:
                await cursor.forward(offset)
            boards = await cursor.many(limit)
        return boards


board_repo = BoardsRepository()
