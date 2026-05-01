from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
import random
from datetime import date

from app.database import get_db
from app.schemas.quiz import (
    QuizCardCreate, QuizCardUpdate, QuizCardResponse,
    QuizStudyCard, QuizAnswerSubmit, QuizAnswerResult
)
from app.models.quiz_card import QuizCard
from app.models.quiz_progress import QuizProgress
from app.models.deck import Deck
from app.models.card import Card
from app.models.user import User
from app.utils.dependencies import get_current_user
from app.services.groq_service import groq_service
from app.utils.spaced_repetition import calculate_next_review
from pydantic import BaseModel

router = APIRouter(prefix="/quiz", tags=["quiz"])

class QuizBulkGenerateRequest(BaseModel):
    topic: str
    details: str = ""
    count: int = 5
    create_new_deck: bool = True

@router.post("/decks/{deck_id}/cards", response_model=QuizCardResponse, status_code=status.HTTP_201_CREATED)
async def create_quiz_card(
    deck_id: int,
    card_data: QuizCardCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создать Quiz карточку"""
    # Проверяем что колода принадлежит пользователю
    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == current_user.id
    ).first()

    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")

    wrong_answers = card_data.wrong_answers or []

    # Генерация неправильных ответов через AI
    if card_data.generate_wrong_with_ai and len(wrong_answers) < 3:
        needed = 3 - len(wrong_answers)
        ai_wrong = await groq_service.generate_wrong_answers(
            card_data.question,
            card_data.correct_answers[0],
            count=needed
        )
        wrong_answers.extend(ai_wrong)

    # Если AI не сработал или не хватает - берем из других карточек
    if len(wrong_answers) < 3 and card_data.source_deck_id:
        source_cards = db.query(Card).filter(
            Card.deck_id == card_data.source_deck_id
        ).all()

        available_answers = [c.back for c in source_cards if c.back not in card_data.correct_answers]
        random.shuffle(available_answers)

        needed = 3 - len(wrong_answers)
        wrong_answers.extend(available_answers[:needed])

    # Убедимся что есть минимум 3 неправильных ответа
    if len(wrong_answers) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недостаточно неправильных ответов. Добавьте вручную или выберите колоду-источник."
        )

    new_card = QuizCard(
        deck_id=deck_id,
        source_deck_id=card_data.source_deck_id,
        question=card_data.question,
        correct_answers=card_data.correct_answers,
        wrong_answers=wrong_answers[:3],  # Берем только 3
        is_multiple=card_data.is_multiple,
        explanation=card_data.explanation
    )

    db.add(new_card)
    db.commit()
    db.refresh(new_card)

    return new_card

@router.post("/decks/{deck_id}/cards/bulk-generate", response_model=List[QuizCardResponse], status_code=status.HTTP_201_CREATED)
async def bulk_generate_quiz_cards(
    deck_id: int,
    request: QuizBulkGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Массовая генерация Quiz карточек через AI"""

    # Если нужно создать новую колоду
    if request.create_new_deck:
        # Создаем новую колоду с названием темы
        new_deck = Deck(
            user_id=current_user.id,
            name=f"Quiz: {request.topic}",
            description=f"Автоматически созданная Quiz-колода по теме: {request.topic}"
        )
        db.add(new_deck)
        db.flush()
        target_deck_id = new_deck.id
    else:
        # Используем существующую колоду
        deck = db.query(Deck).filter(
            Deck.id == deck_id,
            Deck.user_id == current_user.id
        ).first()

        if not deck:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")

        target_deck_id = deck_id

    # Генерируем карточки через AI
    generated_cards = await groq_service.generate_quiz_cards(
        topic=request.topic,
        details=request.details,
        count=request.count
    )

    if not generated_cards:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось сгенерировать карточки через AI. Проверьте GROQ_API_KEY."
        )

    # Создаем карточки в базе
    created_cards = []
    for card_data in generated_cards:
        new_card = QuizCard(
            deck_id=target_deck_id,
            question=card_data["question"],
            correct_answers=[card_data["correct_answer"]],
            wrong_answers=card_data["wrong_answers"][:3],
            is_multiple=False,
            explanation=card_data.get("explanation")
        )
        db.add(new_card)
        created_cards.append(new_card)

    db.commit()

    # Обновляем все карточки
    for card in created_cards:
        db.refresh(card)

    return created_cards

@router.get("/decks/{deck_id}/progress")
def get_quiz_progress(
    deck_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить прогресс Quiz для колоды"""
    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == current_user.id
    ).first()

    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")

    # Получаем все Quiz карточки колоды
    total_cards = db.query(QuizCard).filter(QuizCard.deck_id == deck_id).count()

    # Получаем количество отвеченных карточек (с прогрессом)
    answered_cards = db.query(QuizProgress).join(
        QuizCard,
        QuizProgress.quiz_card_id == QuizCard.id
    ).filter(
        QuizCard.deck_id == deck_id,
        QuizProgress.user_id == current_user.id,
        QuizProgress.total_count > 0
    ).count()

    return {
        "total_cards": total_cards,
        "answered_cards": answered_cards,
        "progress_percentage": round((answered_cards / total_cards * 100) if total_cards > 0 else 0, 1)
    }

@router.get("/decks/{deck_id}/cards", response_model=List[QuizCardResponse])
def get_quiz_cards(
    deck_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить все Quiz карточки колоды"""
    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == current_user.id
    ).first()

    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")

    cards = db.query(QuizCard).filter(QuizCard.deck_id == deck_id).all()
    return cards

@router.get("/study/{deck_id}/next", response_model=QuizStudyCard)
def get_next_quiz_card(
    deck_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить следующую Quiz карточку для изучения"""
    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == current_user.id
    ).first()

    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")

    # Ищем карточки с прогрессом, которые нужно повторить
    due_card = db.query(QuizCard, QuizProgress).join(
        QuizProgress,
        and_(
            QuizProgress.quiz_card_id == QuizCard.id,
            QuizProgress.user_id == current_user.id
        )
    ).filter(
        QuizCard.deck_id == deck_id,
        QuizProgress.due_date <= date.today()
    ).first()

    if due_card:
        card, progress = due_card
    else:
        # Ищем новые карточки без прогресса
        card = db.query(QuizCard).outerjoin(
            QuizProgress,
            and_(
                QuizProgress.quiz_card_id == QuizCard.id,
                QuizProgress.user_id == current_user.id
            )
        ).filter(
            QuizCard.deck_id == deck_id,
            QuizProgress.id == None
        ).first()

        if not card:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No cards to study")

        progress = None

    # Перемешиваем варианты ответов
    all_options = card.correct_answers + card.wrong_answers
    random.shuffle(all_options)

    return QuizStudyCard(
        id=card.id,
        deck_id=card.deck_id,
        question=card.question,
        options=all_options,
        is_multiple=card.is_multiple,
        progress_id=progress.id if progress else None,
        ease_factor=progress.ease_factor if progress else 2.5,
        interval_days=progress.interval_days if progress else 0,
        repetitions=progress.repetitions if progress else 0,
        due_date=str(progress.due_date if progress else date.today())
    )

@router.post("/study/review/{card_id}", response_model=QuizAnswerResult)
def review_quiz_card(
    card_id: int,
    answer_data: QuizAnswerSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Проверить ответ на Quiz карточку"""
    card = db.query(QuizCard).join(Deck, QuizCard.deck_id == Deck.id).filter(
        QuizCard.id == card_id,
        Deck.user_id == current_user.id
    ).first()

    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

    # Проверяем правильность ответа
    selected_set = set(answer_data.selected_answers)
    correct_set = set(card.correct_answers)
    is_correct = selected_set == correct_set

    # Получаем или создаем прогресс
    progress = db.query(QuizProgress).filter(
        QuizProgress.quiz_card_id == card_id,
        QuizProgress.user_id == current_user.id
    ).first()

    if not progress:
        progress = QuizProgress(
            user_id=current_user.id,
            quiz_card_id=card_id,
            ease_factor=2.5,
            interval_days=0,
            repetitions=0,
            due_date=date.today(),
            correct_count=0,
            total_count=0
        )
        db.add(progress)
        db.flush()

    # Обновляем статистику
    progress.total_count += 1
    if is_correct:
        progress.correct_count += 1

    # Рассчитываем следующее повторение (как "good" если правильно, "again" если нет)
    rating = "good" if is_correct else "again"
    next_review = calculate_next_review(
        rating=rating,
        ease_factor=progress.ease_factor,
        interval_days=progress.interval_days,
        repetitions=progress.repetitions
    )

    progress.ease_factor = next_review['ease_factor']
    progress.interval_days = next_review['interval_days']
    progress.repetitions = next_review['repetitions']
    progress.due_date = next_review['due_date']

    db.commit()

    return QuizAnswerResult(
        correct=is_correct,
        correct_answers=card.correct_answers,
        selected_answers=answer_data.selected_answers,
        explanation=card.explanation
    )

@router.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quiz_card(
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удалить Quiz карточку"""
    card = db.query(QuizCard).join(Deck).filter(
        QuizCard.id == card_id,
        Deck.user_id == current_user.id
    ).first()

    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

    db.delete(card)
    db.commit()

    return None
