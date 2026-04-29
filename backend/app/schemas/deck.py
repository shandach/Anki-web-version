from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DeckCreate(BaseModel):
    name: str
    description: Optional[str] = None

class DeckUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class DeckResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    cards_count: Optional[int] = 0
    due_cards_count: Optional[int] = 0

    class Config:
        from_attributes = True
