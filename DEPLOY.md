# 🚀 Деплой Anki на Vercel + Supabase

## ✅ Что уже готово:

- `/api/index.py` — точка входа FastAPI для Vercel
- `/requirements.txt` — зависимости Python
- `/vercel.json` — конфигурация маршрутов
- `frontend/.env.production` — API URL для продакшена
- Код уже поддерживает PostgreSQL (через SQLAlchemy)

---

## 📋 Пошаговая инструкция:

### Шаг 1: Создайте БД на Supabase (5 минут)

1. Зайдите на https://supabase.com
2. **Sign up** / **Log in**
3. **New Project**:
   - Name: `anki-web`
   - Database Password: (сохраните!)
   - Region: выберите ближайший
4. Дождитесь создания (~2 минуты)
5. Перейдите в **Settings → Database**
6. Скопируйте **Connection string** (URI mode):
   ```
   postgresql://postgres.[ref]:[password]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
   ```

### Шаг 2: Настройте локально (тест)

```bash
cd /Users/beckham/omniroutefreeclaude/Anki-proj/backend

# Откройте .env и замените DATABASE_URL на ваш Supabase URL
# DATABASE_URL=postgresql://postgres.[ref]:[password]@...

# Запустите миграции
alembic upgrade head

# Заполните тестовыми данными
python seed_data.py

# Запустите сервер для проверки
uvicorn app.main:app --reload
```

Откройте http://localhost:8000/health — должно вернуть `{"status": "ok"}`

### Шаг 3: Деплой на Vercel

```bash
# Установите Vercel CLI (если еще нет)
npm i -g vercel

# Войдите
vercel login

# Деплой
cd /Users/beckham/omniroutefreeclaude/Anki-proj
vercel
```

**Во время деплоя:**
- Link to existing project? → **No**
- Project name? → `anki-web` (или свое)
- Directory? → `./` (корень)

### Шаг 4: Добавьте переменные окружения в Vercel

После деплоя:

1. Откройте ваш проект на https://vercel.com/dashboard
2. **Settings → Environment Variables**
3. Добавьте:

```
DATABASE_URL = postgresql://postgres.[ref]:[password]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
SECRET_KEY = your-secret-key-change-this-to-random-string
GROQ_API_KEY = your-groq-api-key-here
```

4. **Save**
5. **Redeploy** проект (Deployments → три точки → Redeploy)

### Шаг 5: Проверка

После деплоя:
- Frontend: `https://your-project.vercel.app/`
- API Health: `https://your-project.vercel.app/api/health`

---

## 🔧 Troubleshooting

### Ошибка: "No fastapi entrypoint found"
✅ Решено — создан `/api/index.py`

### Ошибка: "Module not found: app.main"
Проверьте что `requirements.txt` в корне проекта

### База данных пустая
```bash
# Локально запустите с DATABASE_URL из Vercel:
cd backend
DATABASE_URL="postgresql://..." alembic upgrade head
DATABASE_URL="postgresql://..." python seed_data.py
```

### Frontend не подключается к API
Проверьте `frontend/.env.production`:
```
NEXT_PUBLIC_API_URL=/api
```

---

## 💰 Лимиты бесплатного плана:

**Vercel:**
- 100 GB bandwidth/месяц
- 6000 минут выполнения/месяц
- Serverless timeout: 10 секунд

**Supabase:**
- 500 MB database
- 2 GB bandwidth/месяц
- Автобэкапы (7 дней)

---

## 🎯 Следующие шаги:

1. Настройте custom domain (опционально)
2. Добавьте мониторинг (Vercel Analytics)
3. Настройте CI/CD (автодеплой при push в main)

Готово! 🎉
