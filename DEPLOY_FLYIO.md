# Деплой на Fly.io

## Подготовка

### 1. Установка Fly CLI

```bash
# macOS
brew install flyctl

# Linux
curl -L https://fly.io/install.sh | sh

# Windows
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

### 2. Авторизация

```bash
flyctl auth login
```

## Деплой Backend

### 1. Перейдите в папку backend

```bash
cd backend
```

### 2. Инициализация приложения (если еще не сделано)

```bash
flyctl launch --no-deploy
```

При запросе:
- **App name:** выберите уникальное имя (например: `anki-web-api`)
- **Region:** выберите ближайший регион
- **PostgreSQL:** НЕТ (мы используем SQLite)
- **Redis:** НЕТ

### 3. Настройка fly.toml

Убедитесь, что файл `fly.toml` содержит правильные настройки:

```toml
app = "anki-web-api"  # ваше имя приложения
primary_region = "ams"  # ваш регион

[build]
  dockerfile = "Dockerfile"

[env]
  DATABASE_URL = "sqlite:///./anki.db"
  SECRET_KEY = "your-secret-key-here-change-in-production"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = "stop"
  auto_start_machines = true
  min_machines_running = 0
  processes = ["app"]

[[http_service.checks]]
  grace_period = "10s"
  interval = "30s"
  method = "GET"
  timeout = "5s"
  path = "/health"

[[vm]]
  memory = "256mb"
  cpu_kind = "shared"
  cpus = 1
```

### 4. Создание секретов (переменные окружения)

```bash
# Генерируем случайный SECRET_KEY
flyctl secrets set SECRET_KEY=$(openssl rand -hex 32)

# Или установите свой
flyctl secrets set SECRET_KEY="your-very-secret-key-here"
```

### 5. Деплой

```bash
flyctl deploy
```

### 6. Проверка

```bash
# Проверить статус
flyctl status

# Посмотреть логи
flyctl logs

# Открыть в браузере
flyctl open
```

Ваш API будет доступен по адресу: `https://anki-web-api.fly.dev`

## Настройка Frontend для работы с Fly.io

### 1. Обновите переменную окружения

В Vercel/Netlify (где задеплоен frontend):

```
NEXT_PUBLIC_API_URL=https://anki-web-api.fly.dev
```

### 2. Или локально для тестирования

```bash
cd frontend
echo "NEXT_PUBLIC_API_URL=https://anki-web-api.fly.dev" > .env.local
npm run dev
```

## Миграции базы данных

После первого деплоя нужно применить миграции:

```bash
# Подключиться к машине
flyctl ssh console

# Внутри контейнера
cd /app
alembic upgrade head

# Опционально: заполнить тестовыми данными
python seed_data.py

# Выйти
exit
```

## Управление приложением

### Масштабирование

```bash
# Увеличить память
flyctl scale memory 512

# Увеличить количество машин
flyctl scale count 2
```

### Мониторинг

```bash
# Логи в реальном времени
flyctl logs -a anki-web-api

# Метрики
flyctl dashboard
```

### Обновление

```bash
# После изменений в коде
git pull
flyctl deploy
```

## Troubleshooting

### Проблема: Приложение не запускается

```bash
# Проверить логи
flyctl logs

# Проверить статус машин
flyctl status

# Перезапустить
flyctl apps restart anki-web-api
```

### Проблема: База данных пустая

```bash
# Подключиться и применить миграции
flyctl ssh console
alembic upgrade head
python seed_data.py
exit
```

### Проблема: CORS ошибки

Убедитесь, что в `backend/app/main.py` добавлен домен frontend:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-frontend.vercel.app"  # добавьте ваш домен
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Стоимость

- **Free tier:** 3 shared-cpu-1x machines с 256MB RAM
- **Автоматическая остановка:** машины останавливаются при отсутствии трафика
- **Автоматический запуск:** машины запускаются при первом запросе

Для небольшого проекта это бесплатно! 🎉

## Полезные команды

```bash
# Список приложений
flyctl apps list

# Удалить приложение
flyctl apps destroy anki-web-api

# SSH доступ
flyctl ssh console

# Посмотреть конфигурацию
flyctl config show

# Посмотреть секреты
flyctl secrets list
```

## Альтернативные платформы

Если Fly.io не подходит, можно использовать:

1. **Render.com** - аналогичный процесс, бесплатный tier
2. **Railway.app** - простой деплой, $5/месяц
3. **Heroku** - классика, но платный
4. **DigitalOcean App Platform** - от $5/месяц

Dockerfile совместим со всеми этими платформами!
