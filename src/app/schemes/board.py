from typing import List, Optional
from pydantic import BaseModel,  constr


class BoardBase(BaseModel):
    """
    Base model
    """
    title: constr(min_length=1, max_length=100)


class Board(BoardBase):
    """
    Model to return board's information
    """
    id: int
    owner_id: int
    public: bool
    # users: List[User] = []

    class Config:
        orm_mode = True


class BoardCreate(BoardBase):
    """
    Model to create new board
    """
    public: Optional[bool] = False
