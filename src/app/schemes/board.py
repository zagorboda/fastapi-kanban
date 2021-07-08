from typing import List
from pydantic import BaseModel

from .user import User


class BoardBase(BaseModel):
    title: str


class Board(BoardBase):
    id: int
    owner_id: int
    users: List[User] = []

    class Config:
        orm_mode = True


class BoardCreate(BoardBase):
    pass
