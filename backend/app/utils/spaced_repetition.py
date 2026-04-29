from datetime import date, timedelta, datetime

def calculate_next_review(
    rating: str,
    ease_factor: float,
    interval_days: int,
    repetitions: int,
    state: str = "new",
    learning_step: int = 0
):
    """
    Enhanced Anki SM-2 algorithm for spaced repetition

    States:
    - new: карточка никогда не изучалась
    - learning: карточка в процессе первичного изучения (короткие интервалы)
    - review: карточка в режиме повторений (длинные интервалы)
    - relearning: карточка забыта и переучивается

    Learning steps: [1min, 10min] для новых карточек
    Relearning steps: [10min] для забытых карточек

    rating: 'again', 'hard', 'good', 'easy'
    """

    new_state = state
    new_learning_step = learning_step
    new_repetitions = repetitions
    new_ease_factor = ease_factor
    new_interval = interval_days

    # Новая карточка или в процессе обучения
    if state == "new" or state == "learning":
        if rating == "again":
            # Сброс на первый шаг обучения
            new_state = "learning"
            new_learning_step = 0
            new_interval = 0  # <1 минута (в минутах будет 1)
            new_repetitions = 0
            new_ease_factor = max(1.3, ease_factor - 0.2)

        elif rating == "hard":
            # Повтор текущего шага или небольшое увеличение
            new_state = "learning"
            if learning_step == 0:
                new_learning_step = 0
                new_interval = 0  # 6 минут
            else:
                new_learning_step = 1
                new_interval = 0  # 10 минут
            new_ease_factor = max(1.3, ease_factor - 0.15)

        elif rating == "good":
            # Переход к следующему шагу обучения
            new_state = "learning"
            new_learning_step = learning_step + 1

            if new_learning_step == 1:
                new_interval = 0  # 10 минут
            elif new_learning_step >= 2:
                # Переход в режим повторений
                new_state = "review"
                new_interval = 1  # 1 день
                new_repetitions = 1
                new_ease_factor = min(2.5, ease_factor + 0.15)  # Бонус за успешное обучение

        elif rating == "easy":
            # Сразу в режим повторений с большим интервалом
            new_state = "review"
            new_learning_step = 0
            new_interval = 4  # 4 дня
            new_repetitions = 1
            new_ease_factor = ease_factor + 0.15

    # Карточка в режиме повторений
    elif state == "review":
        if rating == "again":
            # Карточка забыта - переход в режим переобучения
            new_state = "relearning"
            new_learning_step = 0
            new_interval = 0  # 10 минут
            new_repetitions = 0
            new_ease_factor = max(1.3, ease_factor - 0.2)

        elif rating == "hard":
            # Интервал увеличивается медленнее
            new_state = "review"
            new_repetitions = repetitions + 1
            new_interval = max(1, int(interval_days * 1.2))
            new_ease_factor = max(1.3, ease_factor - 0.15)

        elif rating == "good":
            # Стандартное увеличение интервала
            new_state = "review"
            new_repetitions = repetitions + 1

            if new_repetitions == 1:
                new_interval = 1
            elif new_repetitions == 2:
                new_interval = 6
            else:
                new_interval = max(1, int(interval_days * ease_factor))

            # EF растет при ранних успехах (первые 3-4 повторения)
            if new_repetitions <= 3:
                new_ease_factor = min(2.5, ease_factor + 0.15)
            else:
                new_ease_factor = ease_factor

        elif rating == "easy":
            # Быстрое увеличение интервала
            new_state = "review"
            new_repetitions = repetitions + 1

            if new_repetitions == 1:
                new_interval = 4
            elif new_repetitions == 2:
                new_interval = 10
            else:
                new_interval = max(1, int(interval_days * ease_factor * 1.3))

            new_ease_factor = ease_factor + 0.15

    # Карточка в режиме переобучения
    elif state == "relearning":
        if rating == "again":
            # Остаемся на первом шаге переобучения
            new_state = "relearning"
            new_learning_step = 0
            new_interval = 0  # 10 минут
            new_ease_factor = max(1.3, ease_factor - 0.2)

        elif rating == "hard":
            # Повтор шага переобучения
            new_state = "relearning"
            new_learning_step = 0
            new_interval = 0  # 10 минут
            new_ease_factor = max(1.3, ease_factor - 0.15)

        elif rating == "good":
            # Возврат в режим повторений с коротким интервалом
            new_state = "review"
            new_learning_step = 0
            new_interval = 1  # 1 день
            new_repetitions = 1

        elif rating == "easy":
            # Возврат в режим повторений с более длинным интервалом
            new_state = "review"
            new_learning_step = 0
            new_interval = 4  # 4 дня
            new_repetitions = 1
            new_ease_factor = ease_factor + 0.15

    else:
        raise ValueError(f"Invalid state: {state}")

    # Ограничение ease_factor
    new_ease_factor = max(1.3, min(2.5, new_ease_factor))

    # Вычисление due_date
    if new_interval == 0:
        # Для внутридневных интервалов используем текущее время + минуты
        # В упрощенной версии ставим на сегодня
        new_due_date = date.today()
    else:
        new_due_date = date.today() + timedelta(days=new_interval)

    return {
        'ease_factor': new_ease_factor,
        'interval_days': new_interval,
        'repetitions': new_repetitions,
        'due_date': new_due_date,
        'state': new_state,
        'learning_step': new_learning_step
    }
