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
    owner_id: int
    list_id: int
    created_at: datetime
    last_changed_at: datetime
    last_change_by_id: int

    class Config:
        orm_mode = True
