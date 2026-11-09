FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEMO_READ_ONLY=true

WORKDIR /app

COPY backend/requirements.txt backend/requirements.txt
RUN python -m pip install --no-cache-dir --requirement backend/requirements.txt

COPY backend/app backend/app
COPY frontend/index.html frontend/index.html
COPY frontend/styles.css frontend/styles.css
COPY frontend/js frontend/js

WORKDIR /app/backend

CMD ["python", "-m", "app.startup"]
