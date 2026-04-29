"""
Script to initialize progress for existing cards
"""
from datetime import date
from app.database import SessionLocal
from app.models.card import Card
from app.models.progress import Progress
from app.models.user import User

def init_progress():
    db = SessionLocal()

    try:
        # Get all users
        users = db.query(User).all()

        for user in users:
            # Get all cards
            cards = db.query(Card).all()

            for card in cards:
                # Check if progress already exists
                existing = db.query(Progress).filter(
                    Progress.user_id == user.id,
                    Progress.card_id == card.id
                ).first()

                if not existing:
                    # Create new progress with due_date = today (ready to study)
                    progress = Progress(
                        user_id=user.id,
                        card_id=card.id,
                        ease_factor=2.5,
                        interval_days=0,
                        repetitions=0,
                        due_date=date.today()  # Ready to study today
                    )
                    db.add(progress)
                    print(f"✅ Created progress for user {user.email}, card {card.id}")

        db.commit()
        print("\n🎉 Progress initialized for all cards!")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_progress()
