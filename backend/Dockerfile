FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY scripts ./scripts
COPY data ./data

ENV DATABASE_PATH=data/wind_jan2026.db
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Prefer seed DB on boot if live DB missing
CMD ["sh", "-c", "python -c \"from app.services.store import Store; Store().ensure_db()\" && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
