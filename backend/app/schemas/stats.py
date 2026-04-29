from pydantic import BaseModel
from typing import Optional

class DashboardStats(BaseModel):
    total_decks: int
    total_cards: int
    due_today: int
    studied_today: int
    streak_days: int
    accuracy_percent: Optional[float] = 0.0

class RecentReview(BaseModel):
    card_front: str
    deck_name: str
    rating: str
    reviewed_at: str
