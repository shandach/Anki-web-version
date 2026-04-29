from pydantic import BaseModel
from datetime import datetime

class CardCreate(BaseModel):
    front: str
    back: str

class CardUpdate(BaseModel):
    front: str
    back: str

class CardResponse(BaseModel):
    id: int
    deck_id: int
    front: str
    back: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
