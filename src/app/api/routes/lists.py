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
        title: str = Body(..., embed=True)
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

    return list_schema.ListModel(
        **new_list.to_dict(),
        **{
            'url': await list_repo.get_list_url(board_id=board_id, list_id=new_list.id),
            'cards_url': await list_repo.get_cards_url(board_id=board_id, list_id=new_list.id),
        }
    )


@router.get("/{board_id}/lists", name="list:get-lists")
async def get_lists(
        board_id: int,
        current_user: User = Depends(get_current_active_or_unauthenticated_user),
        offset: int = 0,
        limit: int = 25
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

    lists = await list_repo.get_multiple_lists(board_id=board_id, offset=offset, limit=limit)

    response = []

    # TODO: create separate function to convert model objects to json list
    for lst in lists:
        response.append(
            list_schema.ListModel(
                **lst.to_dict(),
                **{
                    'url': await list_repo.get_list_url(board_id=board_id, list_id=lst.id),
                    'cards_url': await list_repo.get_cards_url(board_id=board_id, list_id=lst.id)
                }
            )
        )

    return response


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
            detail="Board not found."
        )

    user_is_collaborator = False

    if current_user:
        user_is_collaborator = await board_repo.check_user_is_board_collaborator(
            user_id=current_user.id, board_id=board.id
        )

    if not board.public and not (current_user and user_is_collaborator):
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Board not found."
        )

    requested_list = await list_repo.get_list_by_id(list_id=list_id)

    return list_schema.ListModel(
        **requested_list.to_dict(),
        **{
            'url': await list_repo.get_list_url(board_id=board_id, list_id=requested_list.id),
            'cards_url': await list_repo.get_cards_url(board_id=board_id, list_id=requested_list.id),
        }
    )
