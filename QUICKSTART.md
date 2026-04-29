# Быстрый старт с SQLite

## Запуск проекта (БЕЗ PostgreSQL!)

### 1. Backend

```bash
cd /Users/beckham/omniroutefreeclaude/Anki-proj/backend

# Активируй виртуальное окружение
source venv/bin/activate

# Если venv еще не создан:
# python3 -m venv venv
# source venv/bin/activate
# pip install -r requirements.txt

# Создай базу данных и таблицы
alembic upgrade head

# Заполни мок данными
python seed_data.py

# Запусти сервер
uvicorn app.main:app --reload
```

Backend запустится на http://localhost:8000

### 2. Frontend (в новом терминале)

```bash
cd /Users/beckham/omniroutefreeclaude/Anki-proj/frontend

# Установи зависимости (если еще не установлены)
npm install --legacy-peer-deps
# или
pnpm install

# Запусти dev сервер
npm run dev
# или
pnpm dev
```

Frontend запустится на http://localhost:3000

### 3. Войди в приложение

Открой http://localhost:3000

**Тестовый аккаунт:**
- Email: `test@example.com`
- Password: `password123`

## Что уже создано (мок данные)

✅ **1 пользователь** (test@example.com)

✅ **3 колоды:**
- English Vocabulary (10 карточек)
- Python Programming (8 карточек)
- Spanish Basics (10 карточек)

✅ **28 карточек** с вопросами и ответами

✅ **5 карточек с прогрессом** (3 карточки готовы к изучению сегодня)

## Что можно делать

1. Войти с тестовым аккаунтом
2. Посмотреть дашборд со статистикой
3. Открыть колоды
4. Начать изучение карточек
5. Создать свои колоды и карточки
6. Зарегистрировать новый аккаунт

## База данных

Используется SQLite - файл `anki.db` создается автоматически в папке backend.
PostgreSQL НЕ НУЖЕН!

## Если нужно сбросить данные

```bash
cd backend
rm anki.db
alembic upgrade head
python seed_data.py
```
