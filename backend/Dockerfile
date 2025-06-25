FROM python:3.13-slim

# Встановлюємо робочу директорію всередині контейнера
WORKDIR /app

# Копіюємо файл requirements.txt та встановлюємо залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код бекенду (папку backend) у поточну директорію /app
COPY backend/ ./

# Копіюємо окремо config.py (припускаємо, що він генерується поза Docker)
COPY config.py ./

# Копіюємо файл .env, якщо він є (для зберігання секретів)
#COPY .env ./

# Відкриваємо порт 8000 для зовнішніх підключень
EXPOSE 8000

# Запускаємо uvicorn на 0.0.0.0:8000 (щоб був доступ ззовні контейнера)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
