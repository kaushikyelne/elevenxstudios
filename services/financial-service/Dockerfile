# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Run stage
FROM python:3.12-slim

WORKDIR /app

# Security: non-root user
RUN groupadd -r financial-service && useradd -r -g financial-service financial-service

COPY --from=builder /install /usr/local
COPY . .

USER financial-service

# Cloud Run expects port 8080 by default, but provides it via PORT env var
ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
