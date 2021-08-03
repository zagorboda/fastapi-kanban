from pydantic import BaseModel,  constr
from typing import List, Optional


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
    url: Optional[str]
    collaborators_url: Optional[str]

    class Config:
        orm_mode = True


class BoardList(BoardBase):
    """
    Model to return list of boards
    """
    id: int
    owner_id: int
    public: bool
    url: str

    class Config:
        orm_mode = True


class BoardCreate(BoardBase):
    """
    Model to create new board
    """
    public: Optional[bool] = False
