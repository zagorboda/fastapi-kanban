from typing import List

from fastapi import APIRouter, Body, Depends, Request

from pydantic import parse_obj_as

from app.db.database import db
from app.db.models import User, Board, BoardUsers
from app.db.repositories.boards import board_repo
from app.db.repositories.lists import list_repo
from app.dependencies.auth import get_current_active_user, get_user_from_token, get_current_active_or_unauthenticated_user
from app.schemes import list as list_schema
from app.schemes import card as card_schema


router = APIRouter(prefix="/boards", tags=["lists"])


@router.post("/{board_id}/lists", name="list:create-list")
async def create_list(
        *,
        board_id: int,
        current_user: User = Depends(get_current_active_user),
        title: str = Body(..., embed=True),
        request: Request
):
    board = await board_repo.get_board_and_check_permissions(board_id=board_id, current_user=current_user, request=request)

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
        *,
        board_id: int,
        current_user: User = Depends(get_current_active_or_unauthenticated_user),
        offset: int = 0,
        limit: int = 25,
        request: Request
):
    board = await board_repo.get_board_and_check_permissions(board_id=board_id, current_user=current_user, request=request)

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
        *,
        board_id: int,
        list_id: int,
        current_user: User = Depends(get_current_active_or_unauthenticated_user),
        request: Request
):
    board = await board_repo.get_board_and_check_permissions(board_id=board_id, current_user=current_user, request=request)

    requested_list = await list_repo.get_list_by_id_and_check_board_foreign_key(list_id=list_id, board=board)

    return list_schema.ListModel(
        **requested_list.to_dict(),
        **{
            'url': await list_repo.get_list_url(board_id=board_id, list_id=requested_list.id),
            'cards_url': await list_repo.get_cards_url(board_id=board_id, list_id=requested_list.id),
        }
    )


@router.patch("/{board_id}/lists/{list_id}", name="list:update-list")
async def update_list(
        *,
        board_id: int,
        list_id: int,
        current_user: User = Depends(get_current_active_user),
        updated_list: list_schema.ListUpdate = Body(..., embed=True),
        request: Request
):
    board = await board_repo.get_board_and_check_permissions(board_id=board_id, current_user=current_user, request=request)

    lst = await list_repo.get_list_by_id_and_check_board_foreign_key(list_id=list_id, board=board)

    await list_repo.update(lst=lst, updated_list=updated_list)

    return list_schema.ListModel(
        **lst.to_dict(),
        **{
            'url': await list_repo.get_list_url(board_id=board_id, list_id=lst.id),
            'cards_url': await list_repo.get_cards_url(board_id=board_id, list_id=lst.id),
        }
    )


@router.get("/{board_id}/lists/{list_id}/history", name="list:get-list-history")
async def get_list(
        *,
        board_id: int,
        list_id: int,
        current_user: User = Depends(get_current_active_or_unauthenticated_user),
        request: Request,
        offset: int = 0,
        limit: int = 25,
):
    board = await board_repo.get_board_and_check_permissions(board_id=board_id, current_user=current_user, request=request)

    lst = await list_repo.get_list_by_id_and_check_board_foreign_key(list_id=list_id, board=board)

    history_list = await list_repo.get_cards_history(list_id=lst.id, offset=offset, limit=limit)

    return parse_obj_as(
        List[card_schema.CardHistoryRetrieve],
        list(map(db.Model.to_dict, history_list))
    )
