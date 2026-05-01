#!/bin/bash

# Скрипт для миграции на PostgreSQL

echo "🔄 Запуск миграций Alembic для PostgreSQL..."

cd backend

# Проверка что DATABASE_URL указывает на PostgreSQL
if grep -q "postgresql://" .env; then
    echo "✅ PostgreSQL URL найден в .env"

    # Запуск миграций
    alembic upgrade head

    echo "✅ Миграции выполнены!"
    echo ""
    echo "📊 Теперь можно заполнить тестовыми данными:"
    echo "   python seed_data.py"
else
    echo "❌ Ошибка: DATABASE_URL не указывает на PostgreSQL"
    echo "   Обновите .env файл с вашим Supabase URL"
fi
