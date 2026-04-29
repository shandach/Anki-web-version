from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Date, JSON
from sqlalchemy.sql import func
from app.database import Base

class QuizProgress(Base):
    __tablename__ = "quiz_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    quiz_card_id = Column(Integer, ForeignKey("quiz_cards.id", ondelete="CASCADE"), nullable=False)
    ease_factor = Column(Float, default=2.5)
    interval_days = Column(Integer, default=0)
    repetitions = Column(Integer, default=0)
    due_date = Column(Date, nullable=False)
    last_reviewed_at = Column(DateTime)
    correct_count = Column(Integer, default=0)
    total_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
