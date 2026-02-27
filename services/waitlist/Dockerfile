# Build stage — install dependencies
FROM --platform=linux/amd64 python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Run stage
FROM --platform=linux/amd64 python:3.12-slim

WORKDIR /app

# Security: non-root user
RUN groupadd -r waitlist && useradd -r -g waitlist waitlist

COPY --from=builder /install /usr/local
COPY . .

USER waitlist

# Cloud Run expects port 8080
ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
