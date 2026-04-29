# Anki Web Application

Веб-приложение для изучения карточек по методу интервальных повторений.

## Технологии

### Backend
- Python 3.14
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- JWT Authentication

### Frontend
- React / Next.js
- TypeScript
- Tailwind CSS

## Установка и запуск

### Backend

1. Установите PostgreSQL и создайте базу данных:
```bash
createdb anki_db
createuser -P anki_user
```

2. Настройте переменные окружения:
```bash
cd backend
cp .env.example .env
# Отредактируйте .env с вашими данными PostgreSQL
```

3. Установите зависимости:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. Примените миграции:
```bash
alembic upgrade head
```

5. Запустите сервер:
```bash
uvicorn app.main:app --reload
```

API будет доступен на http://localhost:8000

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Приложение будет доступно на http://localhost:3000

## Функционал

- Регистрация и авторизация пользователей
- Создание и управление колодами карточек
- Добавление и редактирование карточек
- Обучение с интервальными повторениями (SM-2 алгоритм)
- Статистика прогресса (streak, accuracy, карточки к повторению)
- История повторений

## API Endpoints

### Auth
- `POST /auth/register` - Регистрация
- `POST /auth/login` - Вход
- `GET /auth/me` - Текущий пользователь

### Decks
- `GET /decks` - Список колод
- `POST /decks` - Создать колоду
- `GET /decks/{deck_id}` - Получить колоду
- `PUT /decks/{deck_id}` - Обновить колоду
- `DELETE /decks/{deck_id}` - Удалить колоду

### Cards
- `GET /decks/{deck_id}/cards` - Список карточек
- `POST /decks/{deck_id}/cards` - Создать карточку
- `PUT /cards/{card_id}` - Обновить карточку
- `DELETE /cards/{card_id}` - Удалить карточку

### Study
- `GET /study/{deck_id}/next` - Следующая карточка для изучения
- `POST /study/review` - Отправить оценку карточки

### Stats
- `GET /stats/dashboard` - Статистика пользователя

## Структура проекта

```
Anki-proj/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── services/
│   │   └── utils/
│   ├── alembic/
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── api/
│   │   ├── hooks/
│   │   └── styles/
│   ├── package.json
│   └── .env
│
└── README.md
```
