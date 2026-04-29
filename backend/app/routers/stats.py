from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case
from datetime import date, datetime, timedelta
from typing import List
from app.database import get_db
from app.schemas.stats import DashboardStats, RecentReview
from app.models.deck import Deck
from app.models.card import Card
from app.models.progress import Progress
from app.models.review import Review
from app.models.user import User
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Total decks
    total_decks = db.query(func.count(Deck.id)).filter(
        Deck.user_id == current_user.id
    ).scalar()

    # Total cards
    total_cards = db.query(func.count(Card.id)).join(Deck).filter(
        Deck.user_id == current_user.id
    ).scalar()

    # Due today
    due_today = db.query(func.count(Progress.id)).filter(
        Progress.user_id == current_user.id,
        Progress.due_date <= date.today()
    ).scalar()

    # Studied today
    today_start = datetime.combine(date.today(), datetime.min.time())
    studied_today = db.query(func.count(Review.id)).filter(
        Review.user_id == current_user.id,
        Review.reviewed_at >= today_start
    ).scalar()

    # Streak calculation
    streak_days = 0
    current_date = date.today()
    while True:
        day_start = datetime.combine(current_date, datetime.min.time())
        day_end = datetime.combine(current_date, datetime.max.time())
        reviews_count = db.query(func.count(Review.id)).filter(
            Review.user_id == current_user.id,
            Review.reviewed_at >= day_start,
            Review.reviewed_at <= day_end
        ).scalar()

        if reviews_count > 0:
            streak_days += 1
            current_date -= timedelta(days=1)
        else:
            break

    # Accuracy calculation
    total_reviews = db.query(func.count(Review.id)).filter(
        Review.user_id == current_user.id
    ).scalar()

    if total_reviews > 0:
        good_reviews = db.query(func.count(Review.id)).filter(
            Review.user_id == current_user.id,
            Review.rating.in_(['good', 'easy'])
        ).scalar()
        accuracy_percent = (good_reviews / total_reviews) * 100
    else:
        accuracy_percent = 0.0

    return DashboardStats(
        total_decks=total_decks or 0,
        total_cards=total_cards or 0,
        due_today=due_today or 0,
        studied_today=studied_today or 0,
        streak_days=streak_days,
        accuracy_percent=round(accuracy_percent, 2)
    )
