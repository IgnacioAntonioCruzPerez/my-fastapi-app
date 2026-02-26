FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Exclude dev/local files if .dockerignore exists
COPY alembic ./alembic
COPY alembic.ini .
COPY app ./app
COPY models.py .
COPY seed_data.py .

EXPOSE 8000

# Default: run app. Override to run migrations: alembic upgrade head && python seed_data.py && uvicorn ...
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
