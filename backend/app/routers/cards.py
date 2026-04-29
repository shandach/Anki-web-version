from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.card import CardCreate, CardUpdate, CardResponse
from app.models.card import Card
from app.models.deck import Deck
from app.models.user import User
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/decks", tags=["cards"])

@router.get("/{deck_id}/cards", response_model=List[CardResponse])
def get_cards(
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

    cards = db.query(Card).filter(Card.deck_id == deck_id).all()
    return cards

@router.post("/{deck_id}/cards", response_model=CardResponse, status_code=status.HTTP_201_CREATED)
def create_card(
    deck_id: int,
    card_data: CardCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == current_user.id
    ).first()

    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")

    new_card = Card(
        deck_id=deck_id,
        front=card_data.front,
        back=card_data.back
    )
    db.add(new_card)
    db.commit()
    db.refresh(new_card)

    return new_card

@router.put("/cards/{card_id}", response_model=CardResponse)
def update_card(
    card_id: int,
    card_data: CardUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    card = db.query(Card).join(Deck).filter(
        Card.id == card_id,
        Deck.user_id == current_user.id
    ).first()

    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

    card.front = card_data.front
    card.back = card_data.back

    db.commit()
    db.refresh(card)

    return card

@router.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card(
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    card = db.query(Card).join(Deck).filter(
        Card.id == card_id,
        Deck.user_id == current_user.id
    ).first()

    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

    db.delete(card)
    db.commit()

    return None
