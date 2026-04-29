from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    card_id = Column(Integer, ForeignKey("cards.id", ondelete="CASCADE"), nullable=False)
    rating = Column(String, nullable=False)
    old_interval_days = Column(Integer)
    new_interval_days = Column(Integer)
    reviewed_at = Column(DateTime, default=func.current_timestamp())
