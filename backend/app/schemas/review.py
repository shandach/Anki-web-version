from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

class ReviewCreate(BaseModel):
    rating: str

class ReviewResponse(BaseModel):
    id: int
    user_id: int
    card_id: int
    rating: str
    old_interval_days: Optional[int]
    new_interval_days: Optional[int]
    reviewed_at: datetime

    class Config:
        from_attributes = True

class StudyCardResponse(BaseModel):
    id: int
    deck_id: int
    front: str
    back: str
    progress_id: Optional[int] = None
    ease_factor: float
    interval_days: int
    repetitions: int
    due_date: date
    state: Optional[str] = "new"
    learning_step: Optional[int] = 0

    class Config:
        from_attributes = True
