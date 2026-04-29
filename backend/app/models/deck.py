from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Deck(Base):
    __tablename__ = "decks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
