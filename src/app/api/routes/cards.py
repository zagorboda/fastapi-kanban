from fastapi import APIRouter, Body, Depends, Request, HTTPException
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_400_BAD_REQUEST,
)

from app.db import models
from app.db.repositories import board_repo, list_repo, card_repo
from app.dependencies.auth import get_current_active_user, get_current_active_or_unauthenticated_user
from app.schemes import card as card_schema


router = APIRouter(prefix="/boards/{board_id}/lists/{list_id}/cards", tags=["cards"])


@router.post("/", name="card:create-card")
async def create_card(
        *,
        board_id: int,
        list_id: int,
        current_user: models.User = Depends(get_current_active_user),
        card: card_schema.CardCreate = Body(..., embed=True),
        request: Request
):
    board = await board_repo.get_board_and_check_permissions(board_id=board_id, current_user=current_user,
                                                             request=request)

    lst = await list_repo.get_list_by_id_and_check_board_foreign_key(list_id=list_id, board=board)

    new_card = await card_repo.create_new_card(
        card=card,
        list_id=lst.id,
        user_id=current_user.id
    )

    return card_schema.Card(**new_card.to_dict())


@router.get("/", name="card:get-cards")
async def get_cards(
        *,
        board_id: int,
        list_id: int,
        current_user: models.User = Depends(get_current_active_or_unauthenticated_user),
        offset: int = 0,
        limit: int = 25,
        request: Request
):
    board = await board_repo.get_board_and_check_permissions(board_id=board_id, current_user=current_user, request=request)

    lst = await list_repo.get_list_by_id_and_check_board_foreign_key(list_id=list_id, board=board)

    cards = await card_repo.get_list_cards(list_id=lst.id, offset=offset, limit=limit)

    response = []

    for card in cards:
        response.append(card_schema.Card(**card.to_dict()))

    return response


@router.get("/{card_id}", name="card:get-card")
async def get_card(
        *,
        board_id: int,
        list_id: int,
        card_id: int,
        current_user: models.User = Depends(get_current_active_or_unauthenticated_user),
        request: Request
):
    board = await board_repo.get_board_and_check_permissions(board_id=board_id, current_user=current_user,
                                                             request=request)

    lst = await list_repo.get_list_by_id_and_check_board_foreign_key(list_id=list_id, board=board)

    card = await card_repo.get_card_by_id_and_check_list_foreign_key(card_id=card_id, lst=lst)

    return card_schema.Card(**card.to_dict())
