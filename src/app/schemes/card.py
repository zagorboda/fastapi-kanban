from datetime import datetime

from typing import Optional
from pydantic import BaseModel


from app.db import enums


class CardBase(BaseModel):
    title: str
    description: Optional[str] = None


class CardCreate(CardBase):
    pass


class Card(CardBase):
    id: int
    list_id: int
    created_at: datetime
    last_change_at: datetime
    last_change_by_id: int

    class Config:
        orm_mode = True


class CardUpdate(CardBase):
    title: Optional[str]
    description: Optional[str] = None

    list_id: Optional[int]


class CardHistory(BaseModel):
    card_id: int
    title: str
    description: Optional[str] = None
    action: enums.CardHistoryActions

    list_id: int
    last_change_by_id: int
    last_change_at: datetime


class CardHistoryRetrieve(CardHistory):
    id: int
