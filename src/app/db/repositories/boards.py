from typing import Optional

from fastapi import HTTPException, status, Body
from pydantic import EmailStr

from app.db import models
from app.db.database import db
from app.schemes import board as board_schema
from app.services import auth_service


class BoardsRepository:
    def __init__(self):
        self.auth_service = auth_service

    async def create_new_board(self, *, board: board_schema.BoardCreate, owner: models.User):
        return await models.Board.create(**board.dict(), **{'owner_id': owner.id})

    async def get_all_public_boards(self, *, offset=0, limit=25):
        async with db.transaction():
            cursor = await models.Board.query.gino.iterate()
            if offset:
                await cursor.forward(offset)
            boards = await cursor.many(limit)
        return boards

