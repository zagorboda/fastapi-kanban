from typing import List

from fastapi import APIRouter, Path, Body, Depends, HTTPException
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
)

from pydantic import parse_obj_as

from app.db.models import User
from app.db.repositories.boards import BoardsRepository
from app.dependencies.auth import get_current_active_user
from app.schemes import board as board_schema


router = APIRouter(prefix="/boards", tags=["boards"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/", name="board:create-new-board", status_code=HTTP_201_CREATED, response_model=board_schema.Board)
async def create_new_board(
    current_user: User = Depends(get_current_active_user),
    board: board_schema.BoardCreate = Body(..., embed=True),
) -> board_schema.Board:
    board = await BoardsRepository().create_new_board(board=board, owner=current_user)
    return board_schema.Board(**board.to_dict())


@router.get("/", name="board:get-all-public-boards")
async def get_all(offset: int = 0, limit: int = 25):
    boards = await BoardsRepository().get_all_public_boards(offset=offset, limit=limit)
    return parse_obj_as(List[board_schema.Board], boards)
