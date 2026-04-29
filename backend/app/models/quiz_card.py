from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.sql import func
from app.database import Base

class QuizCard(Base):
    __tablename__ = "quiz_cards"

    id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, ForeignKey("decks.id", ondelete="CASCADE"), nullable=False)
    source_deck_id = Column(Integer, ForeignKey("decks.id", ondelete="SET NULL"), nullable=True)
    question = Column(Text, nullable=False)
    correct_answers = Column(JSON, nullable=False)  # ["answer1", "answer2"]
    wrong_answers = Column(JSON, nullable=False)    # ["wrong1", "wrong2", "wrong3"]
    is_multiple = Column(Boolean, default=False)    # Можно ли выбрать несколько ответов
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
