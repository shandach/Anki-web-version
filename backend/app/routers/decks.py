from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import date
from app.database import get_db
from app.schemas.deck import DeckCreate, DeckUpdate, DeckResponse
from app.models.deck import Deck
from app.models.card import Card
from app.models.progress import Progress
from app.models.user import User
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/decks", tags=["decks"])

@router.get("", response_model=List[DeckResponse])
def get_decks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    decks = db.query(Deck).filter(Deck.user_id == current_user.id).all()

    result = []
    for deck in decks:
        cards_count = db.query(func.count(Card.id)).filter(Card.deck_id == deck.id).scalar()
        due_cards_count = db.query(func.count(Progress.id)).join(Card).filter(
            Card.deck_id == deck.id,
            Progress.user_id == current_user.id,
            Progress.due_date <= date.today()
        ).scalar()

        deck_dict = {
            "id": deck.id,
            "user_id": deck.user_id,
            "name": deck.name,
            "description": deck.description,
            "created_at": deck.created_at,
            "updated_at": deck.updated_at,
            "cards_count": cards_count,
            "due_cards_count": due_cards_count
        }
        result.append(deck_dict)

    return result

@router.post("", response_model=DeckResponse, status_code=status.HTTP_201_CREATED)
def create_deck(
    deck_data: DeckCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_deck = Deck(
        user_id=current_user.id,
        name=deck_data.name,
        description=deck_data.description
    )
    db.add(new_deck)
    db.commit()
    db.refresh(new_deck)

    return {**new_deck.__dict__, "cards_count": 0, "due_cards_count": 0}

@router.get("/{deck_id}", response_model=DeckResponse)
def get_deck(
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

    cards_count = db.query(func.count(Card.id)).filter(Card.deck_id == deck.id).scalar()
    due_cards_count = db.query(func.count(Progress.id)).join(Card).filter(
        Card.deck_id == deck.id,
        Progress.user_id == current_user.id,
        Progress.due_date <= date.today()
    ).scalar()

    return {**deck.__dict__, "cards_count": cards_count, "due_cards_count": due_cards_count}

@router.put("/{deck_id}", response_model=DeckResponse)
def update_deck(
    deck_id: int,
    deck_data: DeckUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == current_user.id
    ).first()

    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")

    if deck_data.name is not None:
        deck.name = deck_data.name
    if deck_data.description is not None:
        deck.description = deck_data.description

    db.commit()
    db.refresh(deck)

    cards_count = db.query(func.count(Card.id)).filter(Card.deck_id == deck.id).scalar()
    due_cards_count = db.query(func.count(Progress.id)).join(Card).filter(
        Card.deck_id == deck.id,
        Progress.user_id == current_user.id,
        Progress.due_date <= date.today()
    ).scalar()

    return {**deck.__dict__, "cards_count": cards_count, "due_cards_count": due_cards_count}

@router.delete("/{deck_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deck(
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

    db.delete(deck)
    db.commit()

    return None
