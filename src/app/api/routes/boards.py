from typing import List

from fastapi import APIRouter, Path, Body, Depends, HTTPException, Request
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
from app.db.repositories.boards import board_repo
from app.dependencies.auth import get_current_active_user, get_user_from_token, get_current_or_unauthenticated_user
from app.schemes import board as board_schema


router = APIRouter(prefix="/boards", tags=["boards"])

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/", name="board:create-new-board", status_code=HTTP_201_CREATED, response_model=board_schema.Board)
async def create_new_board(
    current_user: User = Depends(get_current_active_user),
    board: board_schema.BoardCreate = Body(..., embed=True),
) -> board_schema.Board:
    board = await board_repo.create_new_board(board=board, owner=current_user)
    return board_schema.Board(**board.to_dict())


@router.get("/", name="board:get-all-public-boards")
async def get_all(offset: int = 0, limit: int = 25):
    boards = await board_repo.get_all_public_boards(offset=offset, limit=limit)

    response = []

    for board in boards:
        response.append(
            board_schema.Board(
                **board.to_dict(),
                **{'url': await board_repo.get_board_url(board.id)}
            )
        )

    return response


@router.get("/me", name="board:get-my-boards")
async def get_all(request: Request, current_user: User = Depends(get_current_active_user), offset: int = 0, limit: int = 25):
    boards = await board_repo.get_my_boards(user=current_user, offset=offset, limit=limit)

    response = []

    for board in boards:
        response.append(
            board_schema.Board(
                **board.to_dict(),
                **{'url': await board_repo.get_board_url(board.id)}
            )
        )

    return response


@router.get("/{id}", name="board:get-board-by-id")
async def get_board(id: int, request: Request, current_user: User = Depends(get_current_or_unauthenticated_user)): # current_user: User = Depends(get_user_from_token)
    # get board from db
    board = await board_repo.get_board(id)

    # raise not found
    if not board:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Board not found."
        )

    # convert model object to pydantic model, add self url
    board = board_schema.Board(
        **board.to_dict(),
        **{'url': await board_repo.get_board_url(board.id)}
    )

    # check if board is public
    if board.public:
        return board

    # check if user authenticated and user is board owner
    if current_user and current_user.id == board.owner_id:
        return board

    # user not authenticated or not owner
    raise HTTPException(
        status_code=HTTP_404_NOT_FOUND,
        detail="Board not found."
    )
