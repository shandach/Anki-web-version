# Anki Web - Spaced Repetition Flashcard App

Full-stack веб-приложение для изучения карточек методом интервальных повторений с полной реализацией алгоритма Anki SM-2.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.14-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-green.svg)
![Next.js](https://img.shields.io/badge/Next.js-16.2-black.svg)
![React](https://img.shields.io/badge/React-19.2-blue.svg)

## 🎯 Особенности

### Алгоритм интервальных повторений
- ✅ Полная реализация алгоритма Anki (модифицированный SuperMemo 2)
- ✅ 4 состояния карточек: New → Learning → Review (с возможностью Relearning)
- ✅ Динамический Ease Factor (1.3 - 2.5), адаптирующийся под память пользователя
- ✅ Шаги обучения [1 мин, 10 мин] и переобучения [10 мин]
- ✅ Точные формулы для всех оценок (Again/Hard/Good/Easy)

### Интерфейс
- ✅ Список колод как главный экран (как в Anki)
- ✅ Визуальные индикаторы для колод с карточками к изучению
- ✅ Функция "Учить всё" для изучения карточек из всех колод сразу
- ✅ Прогнозируемые интервалы на кнопках оценок
- ✅ Отображение состояния карточки (Новая/Обучение/Повторение/Переобучение)

### Функционал
- ✅ Регистрация и авторизация (JWT)
- ✅ Создание и управление колодами
- ✅ Добавление и редактирование карточек
- ✅ Статистика прогресса (streak, accuracy, карточки к повторению)
- ✅ История повторений

## 🛠 Технологии

### Backend
- **Python 3.14**
- **FastAPI 0.136+** - современный веб-фреймворк
- **SQLAlchemy 2.0** - ORM для работы с БД
- **Alembic 1.18** - миграции базы данных
- **SQLite** - база данных (легко переключить на PostgreSQL)
- **JWT** - аутентификация
- **Pydantic** - валидация данных

### Frontend
- **Next.js 16.2** - React фреймворк с App Router
- **React 19.2** - UI библиотека
- **TypeScript 5** - типизация
- **Tailwind CSS 4** - стилизация
- **Axios** - HTTP клиент

## 📦 Установка и запуск

### Требования
- Python 3.14+
- Node.js 18+
- npm или pnpm

### 1. Клонирование репозитория

```bash
git clone https://github.com/shandach/Anki-web-version.git
cd Anki-web-version
```

### 2. Backend

```bash
cd backend

# Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Настроить переменные окружения
cp .env.example .env
# Отредактируйте .env при необходимости

# Применить миграции
alembic upgrade head

# Заполнить тестовыми данными (опционально)
python seed_data.py

# Запустить сервер
uvicorn app.main:app --reload
```

Backend будет доступен на **http://localhost:8000**

### 3. Frontend

```bash
cd frontend

# Установить зависимости
npm install --legacy-peer-deps
# или
pnpm install

# Настроить переменные окружения
cp .env.example .env.local
# По умолчанию API URL: http://localhost:8000

# Запустить dev сервер
npm run dev
# или
pnpm dev
```

Frontend будет доступен на **http://localhost:3000**

## 🚀 Быстрый старт

После запуска обоих серверов:

1. Откройте http://localhost:3000
2. Войдите с тестовым аккаунтом:
   - **Email:** `test@example.com`
   - **Password:** `password123`
3. Вы увидите список колод с количеством карточек к изучению
4. Нажмите "Учить" на конкретной колоде или "Учить всё" для смешанного изучения

### Тестовые данные

После выполнения `seed_data.py` будут созданы:
- 1 пользователь (test@example.com)
- 3 колоды:
  - English Vocabulary (10 карточек)
  - Python Programming (8 карточек)
  - Spanish Basics (10 карточек)
- 28 карточек с вопросами и ответами
- 5 карточек с прогрессом (3 готовы к изучению сегодня)

## 📖 Как работает алгоритм

### Состояния карточек

1. **New (Новая)** - карточка никогда не изучалась
2. **Learning (Обучение)** - короткие интервалы [1 мин, 10 мин]
3. **Review (Повторение)** - длинные интервалы (дни), растут экспоненциально
4. **Relearning (Переобучение)** - карточка забыта, один шаг [10 мин]

### Оценки и их влияние

| Оценка | Интервал | Ease Factor | Описание |
|--------|----------|-------------|----------|
| **Again** | <1 мин / 10 мин | -0.20 | Сброс на начало обучения |
| **Hard** | ×1.2 | -0.15 | Медленный рост интервала |
| **Good** | ×EF | +0.15 (первые 3 раза) | Стандартный рост |
| **Easy** | ×EF×1.3 | +0.15 | Быстрый рост интервала |

### Ease Factor (EF)
- Начальное значение: **2.5**
- Диапазон: **1.3 - 2.5**
- Индивидуален для каждой карточки
- Адаптируется под вашу память

### Пример работы

**Успешное изучение новой карточки:**
1. New → Good → Learning (10 мин, EF=2.5)
2. Learning → Good → Review (1 день, rep=1, EF=2.65)
3. Review → Good → Review (6 дней, rep=2, EF=2.65)
4. Review → Good → Review (15 дней, rep=3, EF=2.65)
5. Review → Good → Review (39 дней, rep=4, EF=2.65)

**Забывание карточки:**
1. Review (15 дней, EF=2.5)
2. → Again → Relearning (10 мин, EF=2.3)
3. Relearning → Good → Review (1 день, EF=2.3)

Подробнее см. [ALGORITHM.md](ALGORITHM.md)

## 📁 Структура проекта

```
Anki-web-version/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI приложение
│   │   ├── config.py            # Настройки
│   │   ├── database.py          # Подключение к БД
│   │   ├── models/              # SQLAlchemy модели
│   │   ├── schemas/             # Pydantic схемы
│   │   ├── routers/             # API endpoints
│   │   └── utils/               # Утилиты (auth, алгоритм)
│   ├── alembic/                 # Миграции БД
│   ├── requirements.txt
│   └── seed_data.py             # Тестовые данные
│
├── frontend/
│   ├── app/                     # Next.js App Router
│   │   ├── login/               # Страница входа
│   │   ├── register/            # Страница регистрации
│   │   ├── dashboard/           # Панель управления
│   │   ├── decks/               # Список колод
│   │   └── study/               # Страницы изучения
│   ├── lib/
│   │   ├── api.ts               # API клиент
│   │   └── types.ts             # TypeScript типы
│   └── package.json
│
├── ALGORITHM.md                 # Подробное описание алгоритма
├── QUICKSTART.md                # Быстрый старт
└── README.md                    # Этот файл
```

## 🔌 API Endpoints

### Authentication
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
- `GET /study/{deck_id}/next` - Следующая карточка из колоды
- `GET /study/all/next` - Следующая карточка из всех колод
- `POST /study/review?card_id={id}` - Отправить оценку

### Stats
- `GET /stats/dashboard` - Статистика пользователя

## 🧪 Тестирование

```bash
cd backend
source venv/bin/activate
python test_algorithm.py
```

Все тесты должны пройти успешно ✅

## 📝 Документация

- [ALGORITHM.md](ALGORITHM.md) - Подробное описание алгоритма интервальных повторений
- [QUICKSTART.md](QUICKSTART.md) - Быстрый старт с SQLite
- [CHANGELOG_ALGORITHM.md](CHANGELOG_ALGORITHM.md) - История изменений алгоритма
- [CHANGELOG_DECK_SELECTION.md](CHANGELOG_DECK_SELECTION.md) - История изменений интерфейса

## 🎨 Скриншоты

### Список колод
Главный экран с визуальными индикаторами для колод с карточками к изучению.

### Изучение карточек
Интерфейс изучения с прогнозируемыми интервалами и отображением состояния карточки.

### Статистика
Панель с прогрессом: streak, accuracy, карточки к повторению.

## 🤝 Вклад в проект

Contributions are welcome! Пожалуйста:
1. Fork репозиторий
2. Создайте feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit изменения (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для подробностей.

## 🙏 Благодарности

- Алгоритм основан на [SuperMemo 2](https://www.supermemo.com/en/archives1990-2015/english/ol/sm2) и [Anki](https://apps.ankiweb.net/)
- Создано с помощью Claude Sonnet 4

## 📧 Контакты

Если у вас есть вопросы или предложения, создайте Issue в репозитории.

---

**Приятного изучения! 🎓**
