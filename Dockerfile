FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x fetch_news_hourly.sh 2>/dev/null || true

CMD python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    (./fetch_news_hourly.sh 2>/dev/null &) && \
    uvicorn core.asgi:application --host 0.0.0.0 --port 8000