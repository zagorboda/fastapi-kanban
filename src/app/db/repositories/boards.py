from fastapi import Depends, Request, HTTPException
from starlette.status import (
    HTTP_404_NOT_FOUND,
)

from app.core import config
from app.db import models
from app.db.database import db
from app.dependencies.auth import get_current_active_user, get_current_active_or_unauthenticated_user
from app.schemes import board as board_schema
from app.services import auth_service


class BoardsRepository:
    def __init__(self):
        self.auth_service = auth_service

    async def get_board_url(self, board_id: int):
        return f'{config.BASE_URL}{config.API_PREFIX}/boards/{board_id}'

    async def get_board_collaborators_url(self, board_id: int):
        return f'{config.BASE_URL}{config.API_PREFIX}/boards/{board_id}/users'

    async def get_board_collaborators(self, *, board_id: int):
        query = models.User.outerjoin(models.BoardUsers).outerjoin(models.Board).select().where(models.Board.id == board_id)

        users = await query.gino.load(
            models.User.distinct(models.User.id).load(
                add_board=models.Board.distinct(models.Board.id).load(
                    add_user=models.User.distinct(models.User.id)
                )
            )
        ).all()

        return users

    async def check_user_is_board_collaborator(self, *, board_id: int, user_id: int):
        board_users_record = await models.BoardUsers.query.where(
            models.BoardUsers.board_id == board_id and
            models.BoardUsers.user_id == user_id
        ).gino.first()

        if board_users_record:
            return True
        return False

    async def add_user_to_board_collaborators(self, *, board_id: int, user_id: int):
        return await models.BoardUsers.create(board_id=board_id, user_id=user_id)

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

    async def get_board_and_check_permissions(
            self,
            *,
            board_id: int,
            current_user: models.User,
            request: Request,
    ):
        board = await self.get_board(board_id)

        # if board not found
        if not board:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Board not found."
            )

        # Check if board is public and request's method is safe
        if board.public and request.method == 'GET':
            return board

        # Check if user in board collaborator
        user_is_collaborator = False
        if current_user:
            user_is_collaborator = await self.check_user_is_board_collaborator(
                user_id=current_user.id, board_id=board.id
            )

        if not user_is_collaborator:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Board not found."
            )

        # If all check pass, return board
        return board


board_repo = BoardsRepository()
