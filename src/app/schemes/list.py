from datetime import datetime
from pydantic import BaseModel,  constr
from typing import Optional


class ListBase(BaseModel):
    """
    Base model
    """
    title: constr(min_length=1, max_length=100)
    board_id: int


class ListModel(ListBase):
    """
    Model to return list
    """
    id: int
    created_by_id: int
    url: Optional[str]
    cards_url: Optional[str]

    class Config:
        orm_mode = True


class MultipleList(ListBase):
    """
    Model to return multiple lists
    """
    id: int
    url: Optional[str]

    class Config:
        orm_mode = True


class ListCreate(ListBase):
    """
    Model to create new list
    """
    pass
