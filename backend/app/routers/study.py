from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, datetime
from app.database import get_db
from app.schemas.review import ReviewCreate, ReviewResponse, StudyCardResponse
from app.models.card import Card
from app.models.deck import Deck
from app.models.progress import Progress
from app.models.review import Review
from app.models.user import User
from app.utils.dependencies import get_current_user
from app.utils.spaced_repetition import calculate_next_review

router = APIRouter(prefix="/study", tags=["study"])

@router.get("/all/next", response_model=StudyCardResponse)
def get_next_card_from_all_decks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get next due card from all user's decks, prioritized by due_date"""

    # Find cards that are due for review across all decks
    due_card = db.query(Card, Progress, Deck).join(
        Progress,
        and_(
            Progress.card_id == Card.id,
            Progress.user_id == current_user.id
        )
    ).join(
        Deck,
        and_(
            Deck.id == Card.deck_id,
            Deck.user_id == current_user.id
        )
    ).filter(
        Progress.due_date <= date.today()
    ).order_by(
        Progress.due_date.asc(),
        Progress.id.asc()
    ).first()

    if due_card:
        card, progress, deck = due_card
        return StudyCardResponse(
            id=card.id,
            deck_id=card.deck_id,
            front=card.front,
            back=card.back,
            progress_id=progress.id,
            ease_factor=progress.ease_factor,
            interval_days=progress.interval_days,
            repetitions=progress.repetitions,
            due_date=progress.due_date,
            state=progress.state or "review",
            learning_step=progress.learning_step or 0
        )

    # Find new cards (no progress yet) from any deck
    new_card = db.query(Card, Deck).outerjoin(
        Progress,
        and_(
            Progress.card_id == Card.id,
            Progress.user_id == current_user.id
        )
    ).join(
        Deck,
        and_(
            Deck.id == Card.deck_id,
            Deck.user_id == current_user.id
        )
    ).filter(
        Progress.id == None
    ).first()

    if new_card:
        card, deck = new_card
        # Create initial progress for new card
        new_progress = Progress(
            user_id=current_user.id,
            card_id=card.id,
            ease_factor=2.5,
            interval_days=0,
            repetitions=0,
            due_date=date.today(),
            state="new",
            learning_step=0
        )
        db.add(new_progress)
        db.commit()
        db.refresh(new_progress)

        return StudyCardResponse(
            id=card.id,
            deck_id=card.deck_id,
            front=card.front,
            back=card.back,
            progress_id=new_progress.id,
            ease_factor=2.5,
            interval_days=0,
            repetitions=0,
            due_date=date.today(),
            state="new",
            learning_step=0
        )

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No cards to study")

@router.get("/{deck_id}/next", response_model=StudyCardResponse)
def get_next_card(
    deck_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == current_user.id
    ).first()

    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")

    # Find cards that are due for review
    due_card = db.query(Card, Progress).join(
        Progress,
        and_(
            Progress.card_id == Card.id,
            Progress.user_id == current_user.id
        )
    ).filter(
        Card.deck_id == deck_id,
        Progress.due_date <= date.today()
    ).first()

    if due_card:
        card, progress = due_card
        return StudyCardResponse(
            id=card.id,
            deck_id=card.deck_id,
            front=card.front,
            back=card.back,
            progress_id=progress.id,
            ease_factor=progress.ease_factor,
            interval_days=progress.interval_days,
            repetitions=progress.repetitions,
            due_date=progress.due_date,
            state=progress.state or "review",
            learning_step=progress.learning_step or 0
        )

    # Find new cards (no progress yet)
    new_card = db.query(Card).outerjoin(
        Progress,
        and_(
            Progress.card_id == Card.id,
            Progress.user_id == current_user.id
        )
    ).filter(
        Card.deck_id == deck_id,
        Progress.id == None
    ).first()

    if new_card:
        # Create initial progress for new card
        new_progress = Progress(
            user_id=current_user.id,
            card_id=new_card.id,
            ease_factor=2.5,
            interval_days=0,
            repetitions=0,
            due_date=date.today(),
            state="new",
            learning_step=0
        )
        db.add(new_progress)
        db.commit()
        db.refresh(new_progress)

        return StudyCardResponse(
            id=new_card.id,
            deck_id=new_card.deck_id,
            front=new_card.front,
            back=new_card.back,
            progress_id=new_progress.id,
            ease_factor=2.5,
            interval_days=0,
            repetitions=0,
            due_date=date.today(),
            state="new",
            learning_step=0
        )

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No cards to study")

@router.post("/review", response_model=ReviewResponse)
def review_card(
    card_id: int,
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    card = db.query(Card).join(Deck).filter(
        Card.id == card_id,
        Deck.user_id == current_user.id
    ).first()

    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

    # Get or create progress
    progress = db.query(Progress).filter(
        Progress.card_id == card_id,
        Progress.user_id == current_user.id
    ).first()

    if not progress:
        progress = Progress(
            user_id=current_user.id,
            card_id=card_id,
            ease_factor=2.5,
            interval_days=0,
            repetitions=0,
            due_date=date.today(),
            state="new",
            learning_step=0
        )
        db.add(progress)
        db.flush()

    old_interval = progress.interval_days

    # Calculate next review
    next_review = calculate_next_review(
        rating=review_data.rating,
        ease_factor=progress.ease_factor,
        interval_days=progress.interval_days,
        repetitions=progress.repetitions,
        state=progress.state or "new",
        learning_step=progress.learning_step or 0
    )

    # Update progress
    progress.ease_factor = next_review['ease_factor']
    progress.interval_days = next_review['interval_days']
    progress.repetitions = next_review['repetitions']
    progress.due_date = next_review['due_date']
    progress.state = next_review['state']
    progress.learning_step = next_review['learning_step']
    progress.last_reviewed_at = datetime.utcnow()

    # Create review record
    review = Review(
        user_id=current_user.id,
        card_id=card_id,
        rating=review_data.rating,
        old_interval_days=old_interval,
        new_interval_days=next_review['interval_days']
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    return review
