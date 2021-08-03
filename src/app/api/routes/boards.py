from typing import List

from fastapi import APIRouter, Path, Body, Depends, HTTPException, Request
from fastapi.exceptions import HTTPException
# from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
)

# from pydantic import parse_obj_as

from app.db.models import User, Board, BoardUsers
from app.db.repositories.boards import board_repo
from app.dependencies.auth import get_current_active_user, get_user_from_token, get_current_active_or_unauthenticated_user
from app.schemes import board as board_schema
from app.schemes import user as user_schema


router = APIRouter(prefix="/boards", tags=["boards"])

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/", name="board:create-new-board", status_code=HTTP_201_CREATED, response_model=board_schema.Board)
async def create_new_board(
    current_user: User = Depends(get_current_active_user),
    board: board_schema.BoardCreate = Body(..., embed=True),
) -> board_schema.Board:
    board = await board_repo.create_new_board(board=board, owner=current_user)

    # add owner to collaborators table
    await board_repo.add_user_to_board_collaborators(
        board_id=board.id,
        user_id=current_user.id
    )

    return board_schema.Board(**board.to_dict())


@router.get("/", name="board:get-all-public-boards")
async def get_all(offset: int = 0, limit: int = 25):
    boards = await board_repo.get_all_public_boards(offset=offset, limit=limit)

    # query = Board.outerjoin(BoardUsers).outerjoin(User).select()
    # boards = await query.gino.load(
    #     Board.distinct(Board.id).load(add_user=User.distinct(User.id))).all()

    # query = User.outerjoin(BoardUsers).outerjoin(Board).select()
    # users = await query.gino.load(
    #     User.distinct(User.id).load(add_user=Board.distinct(Board.id))).all()

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
async def get_my_boards(request: Request, current_user: User = Depends(get_current_active_user), offset: int = 0, limit: int = 25):

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
async def get_board(id: int, current_user: User = Depends(get_current_active_or_unauthenticated_user)):
    # get board from db
    board = await board_repo.get_board(id)

    # if board not found
    if not board:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Board not found."
        )

    user_is_collaborator = False

    if current_user:
        user_is_collaborator = await board_repo.check_user_is_board_collaborator(
            user_id=current_user.id, board_id=board.id
        )

    # if board not public and request user not in users list
    if not board.public and not (current_user and user_is_collaborator):
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Board not found."
        )

    # convert model object to pydantic model, add self url and users url
    board = board_schema.Board(
        **board.to_dict(),
        **{'url': await board_repo.get_board_url(board.id)},
        **{'collaborators_url': await board_repo.get_board_collaborators_url(board.id)}
    )

    return board


@router.get("/{id}/users", name="board:get-board-users")
async def get_board_collaborators(id: int, request: Request, current_user: User = Depends(get_current_active_or_unauthenticated_user)): # current_user: User = Depends(get_user_from_token)
    # get board from db
    board = await board_repo.get_board(id)

    # if board not found
    if not board:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Board not found."
        )

    user_is_collaborator = False

    if current_user:
        user_is_collaborator = await board_repo.check_user_is_board_collaborator(
            user_id=current_user.id, board_id=board.id
        )

    # if board not public and request user not in users list
    if not board.public and not (current_user and user_is_collaborator):
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Board not found."
        )

    query = User.outerjoin(BoardUsers).outerjoin(Board).select()
    db_users = await query.gino.load(
        User.distinct(User.id).load(add_user=Board.distinct(Board.id))).all()

    users = [user_schema.UserPublic(**user.to_dict()) for user in db_users]

    return users
