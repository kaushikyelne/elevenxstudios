# Waitlist Service

Minimal FastAPI microservice for MoneyLane pre-launch waitlist.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/waitlist/join` | Join waitlist (email) |
| GET | `/api/v1/waitlist/health` | Health check |
| GET | `/api/v1/waitlist/count` | Total entries count |

## Local Development

```bash
# From services/waitlist/
pip install -r requirements.txt

# Copy and edit env
cp .env.example .env

# Run migrations (requires Postgres running)
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

## API Docs

Swagger UI available at `http://localhost:8000/docs` when running locally.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL async connection string |
| `NOTIFICATION_SERVICE_URL` | No | Go notification service URL |
| `ADMIN_API_KEY` | No | API key for admin endpoints |
| `CORS_ORIGINS` | No | Comma-separated CORS origins |

## Deployment

Deployed automatically to Cloud Run on push to `master` when files in `services/waitlist/` change. See `.github/workflows/cd-waitlist.yml`.
