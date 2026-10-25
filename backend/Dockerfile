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

# Materialize slim seed DB at the runtime path for cold starts
RUN if [ -f data/seed/wind_jan2026.db ]; then cp data/seed/wind_jan2026.db data/wind_jan2026.db; fi

EXPOSE 8000

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
