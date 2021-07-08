from datetime import datetime

from typing import Optional
from pydantic import BaseModel


class CardBase(BaseModel):
    text: str
    description: Optional[str] = None


class CardCreate(CardBase):
    pass


class Card(CardBase):
    id: int
    owner_id: int
    last_change_user_id: int
    section_id: int
    created_at: datetime
    last_changed_at: datetime

    class Config:
        orm_mode = True
