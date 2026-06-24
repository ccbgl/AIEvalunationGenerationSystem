# Multi-stage Dockerfile

# Build frontend
FROM node:18-slim AS frontend-build
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --silent
COPY frontend/ ./
RUN npm run build

# Build backend
FROM python:3.10-slim
WORKDIR /app

# system deps
RUN apt-get update \
  && apt-get install -y --no-install-recommends gcc build-essential libpq-dev git curl \
  && rm -rf /var/lib/apt/lists/*

# copy backend
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy backend code
COPY backend/ ./backend/

# copy frontend static output
COPY --from=frontend-build /build/dist ./backend/app/static

ENV PYTHONUNBUFFERED=1
ENV MYSQL_URL=""
ENV REDIS_URL="redis://127.0.0.1:6379/0"

EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
