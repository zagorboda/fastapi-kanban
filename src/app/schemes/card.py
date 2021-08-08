from datetime import datetime

from typing import Optional
from pydantic import BaseModel


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
