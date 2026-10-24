FROM python:3.11-slim

# Отключаем буферизацию вывода Python для мгновенного логирования
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Установка системных утилит
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код бэкенда
COPY . .

# Экспортируем порт FastAPI
EXPOSE 8000

# Запуск приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]