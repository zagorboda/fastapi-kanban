from fastapi import APIRouter, Path, Body, Depends, HTTPException, Request
from fastapi.exceptions import HTTPException
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
)

from app.db.models import User, Board, BoardUsers
from app.db.repositories.boards import board_repo
from app.db.repositories.lists import list_repo
from app.dependencies.auth import get_current_active_user, get_user_from_token, get_current_active_or_unauthenticated_user
# from app.schemes import board as board_schema
# from app.schemes import user as user_schema
from app.schemes import list as list_schema


router = APIRouter(prefix="/boards", tags=["lists"])


@router.post("/{board_id}/lists", name="list:create-list")
async def create_list(
        board_id: int,
        current_user: User = Depends(get_current_active_user),
        title: str = Body(..., embed=True),
):
    board = await board_repo.get_board(board_id)

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
    if not board.public and not user_is_collaborator:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Board not found."
        )

    new_list = await list_repo.create_new_list(
        created_by=current_user,
        list_obj=list_schema.ListCreate(**{'title': title, 'board_id': board.id})
    )

    return new_list


@router.get("/{board_id}/lists/{list_id}", name="list:get-list-by-id")
async def get_list(
        board_id: int,
        list_id: int,
        current_user: User = Depends(get_current_active_or_unauthenticated_user)
):
    board = await board_repo.get_board(board_id)

    # if board not found
    if not board:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Board not found.1"
        )

    user_is_collaborator = False

    if current_user:
        user_is_collaborator = await board_repo.check_user_is_board_collaborator(
            user_id=current_user.id, board_id=board.id
        )

    if not board.public and not (current_user and user_is_collaborator):
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Board not found.2"
        )

    response = await list_repo.get_list_by_id(list_id=list_id)

    return response
