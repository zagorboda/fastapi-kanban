from fastapi import APIRouter, Path, Body, Depends, HTTPException, Request
from fastapi.exceptions import HTTPException
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
)

from app.db import models
from app.db.repositories import board_repo, list_repo, card_repo
from app.dependencies.auth import get_current_active_user, get_current_active_or_unauthenticated_user
from app.schemes import card as card_schema


router = APIRouter(prefix="/boards/{board_id}/lists/{list_id}/cards", tags=["cards"])


@router.post("/", name="card:create-card")
async def create_list(
        board_id: int,
        list_id: int,
        current_user: models.User = Depends(get_current_active_user),
        card: card_schema.CardCreate = Body(..., embed=True),
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

    new_card = await card_repo.create_new_card(
        card=card,
        list_id=list_id,
        user_id=current_user.id
    )

    return card_schema.Card(**new_card.to_dict())


@router.get("/", name="card:get-cards")
async def get_cards(
        board_id: int,
        list_id: int,
        current_user: models.User = Depends(get_current_active_or_unauthenticated_user),
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

    cards = await card_repo.get_list_cards(list_id=list_id, offset=offset, limit=limit)

    response = []

    for card in cards:
        response.append(card_schema.Card(**card.to_dict()))

    return response


@router.get("/{card_id}", name="card:get-card")
async def get_card(
        board_id: int,
        list_id: int,
        card_id: int,
        current_user: models.User = Depends(get_current_active_or_unauthenticated_user),
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

    card = await card_repo.get_card(card_id=card_id)

    return card_schema.Card(**card.to_dict())
