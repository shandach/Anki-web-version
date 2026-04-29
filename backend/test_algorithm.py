#!/usr/bin/env python3
"""Тест нового алгоритма интервальных повторений Anki"""

from app.utils.spaced_repetition import calculate_next_review

def test_new_card_flow():
    """Тест потока новой карточки"""
    print("=" * 60)
    print("ТЕСТ: Новая карточка")
    print("=" * 60)

    # Новая карточка, первое изучение
    print("\n1. Новая карточка, оценка 'good':")
    result = calculate_next_review(
        rating="good",
        ease_factor=2.5,
        interval_days=0,
        repetitions=0,
        state="new",
        learning_step=0
    )
    print(f"   State: {result['state']}")
    print(f"   Learning step: {result['learning_step']}")
    print(f"   Interval: {result['interval_days']} дней")
    print(f"   EF: {result['ease_factor']}")

    # Второй шаг обучения
    print("\n2. Второй шаг обучения, оценка 'good':")
    result = calculate_next_review(
        rating="good",
        ease_factor=result['ease_factor'],
        interval_days=result['interval_days'],
        repetitions=result['repetitions'],
        state=result['state'],
        learning_step=result['learning_step']
    )
    print(f"   State: {result['state']}")
    print(f"   Learning step: {result['learning_step']}")
    print(f"   Interval: {result['interval_days']} дней")
    print(f"   EF: {result['ease_factor']}")
    print(f"   Repetitions: {result['repetitions']}")

def test_review_flow():
    """Тест потока повторений"""
    print("\n" + "=" * 60)
    print("ТЕСТ: Карточка в режиме повторений")
    print("=" * 60)

    # Карточка в режиме повторений
    print("\n1. Review карточка, оценка 'good':")
    result = calculate_next_review(
        rating="good",
        ease_factor=2.5,
        interval_days=1,
        repetitions=1,
        state="review",
        learning_step=0
    )
    print(f"   State: {result['state']}")
    print(f"   Interval: {result['interval_days']} дней")
    print(f"   EF: {result['ease_factor']}")
    print(f"   Repetitions: {result['repetitions']}")

    # Следующее повторение
    print("\n2. Следующее повторение, оценка 'good':")
    result = calculate_next_review(
        rating="good",
        ease_factor=result['ease_factor'],
        interval_days=result['interval_days'],
        repetitions=result['repetitions'],
        state=result['state'],
        learning_step=result['learning_step']
    )
    print(f"   State: {result['state']}")
    print(f"   Interval: {result['interval_days']} дней")
    print(f"   EF: {result['ease_factor']}")
    print(f"   Repetitions: {result['repetitions']}")

    # Еще одно повторение
    print("\n3. Еще одно повторение, оценка 'good':")
    result = calculate_next_review(
        rating="good",
        ease_factor=result['ease_factor'],
        interval_days=result['interval_days'],
        repetitions=result['repetitions'],
        state=result['state'],
        learning_step=result['learning_step']
    )
    print(f"   State: {result['state']}")
    print(f"   Interval: {result['interval_days']} дней (должно быть ~15)")
    print(f"   EF: {result['ease_factor']}")
    print(f"   Repetitions: {result['repetitions']}")

def test_forget_flow():
    """Тест забывания карточки"""
    print("\n" + "=" * 60)
    print("ТЕСТ: Забывание карточки")
    print("=" * 60)

    print("\n1. Review карточка, оценка 'again' (забыли):")
    result = calculate_next_review(
        rating="again",
        ease_factor=2.5,
        interval_days=15,
        repetitions=3,
        state="review",
        learning_step=0
    )
    print(f"   State: {result['state']} (должно быть 'relearning')")
    print(f"   Interval: {result['interval_days']} дней")
    print(f"   EF: {result['ease_factor']} (уменьшился на 0.2)")
    print(f"   Repetitions: {result['repetitions']} (сброшено)")

    print("\n2. Relearning, оценка 'good' (вспомнили):")
    result = calculate_next_review(
        rating="good",
        ease_factor=result['ease_factor'],
        interval_days=result['interval_days'],
        repetitions=result['repetitions'],
        state=result['state'],
        learning_step=result['learning_step']
    )
    print(f"   State: {result['state']} (должно быть 'review')")
    print(f"   Interval: {result['interval_days']} дней")
    print(f"   EF: {result['ease_factor']}")

def test_easy_flow():
    """Тест оценки 'easy'"""
    print("\n" + "=" * 60)
    print("ТЕСТ: Оценка 'easy'")
    print("=" * 60)

    print("\n1. Новая карточка, оценка 'easy':")
    result = calculate_next_review(
        rating="easy",
        ease_factor=2.5,
        interval_days=0,
        repetitions=0,
        state="new",
        learning_step=0
    )
    print(f"   State: {result['state']} (должно быть 'review')")
    print(f"   Interval: {result['interval_days']} дней (должно быть 4)")
    print(f"   EF: {result['ease_factor']} (увеличился)")

    print("\n2. Review карточка, оценка 'easy':")
    result = calculate_next_review(
        rating="easy",
        ease_factor=2.5,
        interval_days=6,
        repetitions=2,
        state="review",
        learning_step=0
    )
    print(f"   State: {result['state']}")
    print(f"   Interval: {result['interval_days']} дней (должно быть ~19)")
    print(f"   EF: {result['ease_factor']} (увеличился)")

if __name__ == "__main__":
    test_new_card_flow()
    test_review_flow()
    test_forget_flow()
    test_easy_flow()

    print("\n" + "=" * 60)
    print("✅ Все тесты завершены!")
    print("=" * 60)
