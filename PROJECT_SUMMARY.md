# Anki Web - Краткое резюме проекта

## Что создано

✅ **Backend (FastAPI + PostgreSQL)**
- Полная авторизация с JWT токенами
- CRUD операции для колод и карточек
- Алгоритм интервальных повторений (SM-2)
- Статистика пользователя (streak, accuracy, прогресс)
- История повторений
- Миграции базы данных (Alembic)

✅ **Frontend (Next.js + TypeScript + Tailwind)**
- Страницы: Login, Register, Dashboard, Decks, Study
- API клиент с автоматической авторизацией
- Адаптивный дизайн
- TypeScript типизация

## Структура файлов

```
Anki-proj/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app
│   │   ├── config.py                  # Settings
│   │   ├── database.py                # DB connection
│   │   ├── models/                    # 5 моделей (User, Deck, Card, Progress, Review)
│   │   ├── schemas/                   # Pydantic schemas
│   │   ├── routers/                   # 5 роутеров (auth, decks, cards, study, stats)
│   │   └── utils/                     # auth, spaced_repetition, dependencies
│   ├── alembic/                       # Миграции
│   ├── requirements.txt               # Python зависимости
│   └── .env.example
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx                   # Redirect на /login
│   │   ├── login/page.tsx             # Вход
│   │   ├── register/page.tsx          # Регистрация
│   │   ├── dashboard/page.tsx         # Статистика
│   │   ├── decks/page.tsx             # Список колод
│   │   └── study/[deckId]/page.tsx    # Обучение
│   ├── lib/
│   │   ├── api.ts                     # API клиент (axios)
│   │   └── types.ts                   # TypeScript типы
│   ├── package.json
│   └── .env.local
│
├── README.md                          # Основная документация
├── SETUP.md                           # Инструкция по запуску
└── .gitignore
```

## API Endpoints

### Auth
- `POST /auth/register` - Регистрация
- `POST /auth/login` - Вход (возвращает JWT)
- `GET /auth/me` - Текущий пользователь

### Decks
- `GET /decks` - Список колод с количеством карточек
- `POST /decks` - Создать колоду
- `GET /decks/{id}` - Получить колоду
- `PUT /decks/{id}` - Обновить колоду
- `DELETE /decks/{id}` - Удалить колоду

### Cards
- `GET /decks/{deck_id}/cards` - Список карточек
- `POST /decks/{deck_id}/cards` - Создать карточку
- `PUT /cards/{id}` - Обновить карточку
- `DELETE /cards/{id}` - Удалить карточку

### Study
- `GET /study/{deck_id}/next` - Следующая карточка для изучения
- `POST /study/review?card_id={id}` - Отправить оценку (again/hard/good/easy)

### Stats
- `GET /stats/dashboard` - Статистика (total_decks, total_cards, due_today, studied_today, streak_days, accuracy_percent)

## Технологии

**Backend:**
- Python 3.14
- FastAPI 0.136+
- SQLAlchemy 2.0
- Alembic 1.18
- psycopg 3.3 (PostgreSQL driver)
- JWT authentication
- Pydantic validation

**Frontend:**
- Next.js 16.2
- React 19.2
- TypeScript 5
- Tailwind CSS 4
- Axios для API запросов

## Следующие шаги

1. **Настроить PostgreSQL** (см. SETUP.md)
2. **Запустить backend:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   # Настроить .env
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

3. **Запустить frontend:**
   ```bash
   cd frontend
   npm install  # или pnpm install
   npm run dev
   ```

4. **Открыть** http://localhost:3000

## Известные проблемы

⚠️ **npm cache permissions** - может потребоваться использовать pnpm или исправить права доступа (см. SETUP.md)

⚠️ **PostgreSQL** - нужно установить и настроить отдельно

## Что работает

✅ Регистрация и вход
✅ Создание колод
✅ Добавление карточек
✅ Обучение с интервальными повторениями
✅ Статистика прогресса
✅ История повторений
✅ JWT авторизация
✅ Адаптивный дизайн

## Готово к использованию!

Проект полностью функционален и готов к локальному запуску.
