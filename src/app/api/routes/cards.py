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


router = APIRouter(prefix="/boards/{board_id}/lists/{list_id}", tags=["cards"])


@router.post("/", name="card:create-card")
async def create_list(
        board_id: int,
        list_id: int
):
    pass

