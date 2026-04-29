"""
Script to populate the database with mock data
"""
from datetime import date, timedelta
from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.deck import Deck
from app.models.card import Card
from app.models.progress import Progress
from app.models.review import Review
from app.utils.auth import get_password_hash

def create_mock_data():
    # Create tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Check if data already exists
        existing_user = db.query(User).first()
        if existing_user:
            print("Mock data already exists!")
            return

        # Create test user
        user = User(
            email="test@example.com",
            password_hash=get_password_hash("password123"),
            name="Test User"
        )
        db.add(user)
        db.flush()

        print(f"✅ Created user: {user.email} (password: password123)")

        # Create decks
        deck1 = Deck(
            user_id=user.id,
            name="English Vocabulary",
            description="Common English words and phrases"
        )
        deck2 = Deck(
            user_id=user.id,
            name="Python Programming",
            description="Python concepts and syntax"
        )
        deck3 = Deck(
            user_id=user.id,
            name="Spanish Basics",
            description="Basic Spanish vocabulary"
        )

        db.add_all([deck1, deck2, deck3])
        db.flush()

        print(f"✅ Created {3} decks")

        # Create cards for English Vocabulary
        english_cards = [
            ("Hello", "A greeting"),
            ("Goodbye", "A farewell"),
            ("Thank you", "Expression of gratitude"),
            ("Please", "Polite request word"),
            ("Sorry", "Expression of apology"),
            ("Beautiful", "Pleasing to the eye"),
            ("Happy", "Feeling joy"),
            ("Sad", "Feeling sorrow"),
            ("Friend", "A person you like and trust"),
            ("Family", "Group of related people"),
        ]

        for front, back in english_cards:
            card = Card(deck_id=deck1.id, front=front, back=back)
            db.add(card)

        # Create cards for Python Programming
        python_cards = [
            ("What is a list in Python?", "A mutable ordered collection of items"),
            ("What is a dictionary?", "A collection of key-value pairs"),
            ("What does 'def' keyword do?", "Defines a function"),
            ("What is a tuple?", "An immutable ordered collection"),
            ("What is a lambda function?", "An anonymous function defined with lambda keyword"),
            ("What is list comprehension?", "A concise way to create lists: [x for x in range(10)]"),
            ("What is 'self' in Python?", "Reference to the instance of the class"),
            ("What is '__init__'?", "Constructor method called when object is created"),
        ]

        for front, back in python_cards:
            card = Card(deck_id=deck2.id, front=front, back=back)
            db.add(card)

        # Create cards for Spanish Basics
        spanish_cards = [
            ("Hola", "Hello"),
            ("Adiós", "Goodbye"),
            ("Gracias", "Thank you"),
            ("Por favor", "Please"),
            ("Lo siento", "I'm sorry"),
            ("Sí", "Yes"),
            ("No", "No"),
            ("Buenos días", "Good morning"),
            ("Buenas noches", "Good night"),
            ("¿Cómo estás?", "How are you?"),
        ]

        for front, back in spanish_cards:
            card = Card(deck_id=deck3.id, front=front, back=back)
            db.add(card)

        db.flush()

        print(f"✅ Created {len(english_cards) + len(python_cards) + len(spanish_cards)} cards")

        # Create some progress and reviews for a few cards
        cards = db.query(Card).limit(5).all()
        today = date.today()

        for i, card in enumerate(cards):
            # Create progress
            progress = Progress(
                user_id=user.id,
                card_id=card.id,
                ease_factor=2.5,
                interval_days=i + 1,
                repetitions=i,
                due_date=today - timedelta(days=1) if i < 3 else today + timedelta(days=i)
            )
            db.add(progress)

            # Create review history
            if i < 3:
                review = Review(
                    user_id=user.id,
                    card_id=card.id,
                    rating="good",
                    old_interval_days=0,
                    new_interval_days=1
                )
                db.add(review)

        print(f"✅ Created progress and reviews for 5 cards")

        db.commit()

        print("\n" + "="*50)
        print("🎉 Mock data created successfully!")
        print("="*50)
        print(f"\n📧 Login credentials:")
        print(f"   Email: test@example.com")
        print(f"   Password: password123")
        print(f"\n📚 Created:")
        print(f"   - 1 user")
        print(f"   - 3 decks")
        print(f"   - 28 cards")
        print(f"   - 5 cards with progress (3 due today)")
        print("\n")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_mock_data()
