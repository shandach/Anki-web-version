from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class QuizCardCreate(BaseModel):
    question: str
    correct_answers: List[str]
    wrong_answers: Optional[List[str]] = []
    source_deck_id: Optional[int] = None
    is_multiple: bool = False
    generate_wrong_with_ai: bool = False

class QuizCardUpdate(BaseModel):
    question: Optional[str] = None
    correct_answers: Optional[List[str]] = None
    wrong_answers: Optional[List[str]] = None
    is_multiple: Optional[bool] = None

class QuizCardResponse(BaseModel):
    id: int
    deck_id: int
    source_deck_id: Optional[int]
    question: str
    correct_answers: List[str]
    wrong_answers: List[str]
    is_multiple: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class QuizStudyCard(BaseModel):
    id: int
    deck_id: int
    question: str
    options: List[str]  # Все варианты перемешанные
    is_multiple: bool
    progress_id: Optional[int] = None
    ease_factor: float
    interval_days: int
    repetitions: int
    due_date: str

class QuizAnswerSubmit(BaseModel):
    selected_answers: List[str]

class QuizAnswerResult(BaseModel):
    correct: bool
    correct_answers: List[str]
    selected_answers: List[str]
    explanation: Optional[str] = None
