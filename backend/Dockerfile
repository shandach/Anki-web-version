FROM python:3.11-slim
WORKDIR /app

# Копируем requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install "fastapi[standard]"

# Копируем всё содержимое backend
COPY . .

EXPOSE 8000

# Запуск с использованием переменной PORT от Render
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
