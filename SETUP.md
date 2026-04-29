# Инструкция по запуску Anki Web

## Требования

- Python 3.14+
- Node.js 18+
- PostgreSQL 14+

## Настройка базы данных

1. Установите PostgreSQL (если еще не установлен)
2. Создайте базу данных и пользователя:

```bash
# Войдите в PostgreSQL
psql postgres

# Создайте пользователя и базу данных
CREATE USER anki_user WITH PASSWORD 'your_password';
CREATE DATABASE anki_db OWNER anki_user;
GRANT ALL PRIVILEGES ON DATABASE anki_db TO anki_user;
\q
```

## Backend

1. Перейдите в папку backend:
```bash
cd backend
```

2. Создайте виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Настройте переменные окружения:
```bash
cp .env.example .env
```

Отредактируйте `.env` файл:
```
DATABASE_URL=postgresql+psycopg://anki_user:your_password@localhost:5432/anki_db
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5. Примените миграции:
```bash
alembic upgrade head
```

6. Запустите сервер:
```bash
uvicorn app.main:app --reload
```

Backend будет доступен на http://localhost:8000

API документация: http://localhost:8000/docs

## Frontend

**ВАЖНО:** Из-за проблем с npm cache, установка зависимостей может потребовать дополнительных действий.

### Вариант 1: Исправить права доступа (требует sudo)

```bash
sudo chown -R $(whoami) ~/.npm
cd frontend
npm install
npm run dev
```

### Вариант 2: Использовать другой менеджер пакетов

```bash
cd frontend

# Установите pnpm
npm install -g pnpm

# Установите зависимости через pnpm
pnpm install

# Запустите dev сервер
pnpm dev
```

### Вариант 3: Очистить cache и попробовать снова

```bash
cd frontend
npm cache clean --force
npm install --legacy-peer-deps
npm run dev
```

Frontend будет доступен на http://localhost:3000

## Структура проекта

```
Anki-proj/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI приложение
│   │   ├── config.py         # Настройки
│   │   ├── database.py       # Подключение к БД
│   │   ├── models/           # SQLAlchemy модели
│   │   ├── schemas/          # Pydantic схемы
│   │   ├── routers/          # API endpoints
│   │   └── utils/            # Утилиты (auth, spaced repetition)
│   ├── alembic/              # Миграции БД
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── app/
│   │   ├── login/           # Страница входа
│   │   ├── register/        # Страница регистрации
│   │   ├── dashboard/       # Дашборд со статистикой
│   │   ├── decks/           # Список колод
│   │   └── study/[deckId]/  # Страница обучения
│   ├── lib/
│   │   ├── api.ts           # API клиент
│   │   └── types.ts         # TypeScript типы
│   └── components/          # React компоненты
│
└── README.md
```

## Использование

1. Откройте http://localhost:3000
2. Зарегистрируйтесь
3. Создайте колоду
4. Добавьте карточки
5. Начните обучение!

## Алгоритм интервальных повторений

Приложение использует модифицированный алгоритм SM-2:

- **Again** - карточка показывается снова скоро (1 день)
- **Hard** - маленький интервал (увеличение на 20%)
- **Good** - стандартный интервал (1 день → 6 дней → ease_factor * предыдущий интервал)
- **Easy** - увеличенный интервал (ease_factor * 1.3)

## Troubleshooting

### Backend не запускается

- Проверьте, что PostgreSQL запущен: `pg_isready`
- Проверьте правильность DATABASE_URL в .env
- Убедитесь, что база данных создана

### Frontend не устанавливается

- Попробуйте использовать pnpm вместо npm
- Очистите npm cache: `npm cache clean --force`
- Используйте флаг `--legacy-peer-deps`

### Ошибки CORS

- Убедитесь, что backend запущен на порту 8000
- Проверьте NEXT_PUBLIC_API_URL в frontend/.env.local
