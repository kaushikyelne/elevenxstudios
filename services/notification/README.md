# Notification Service

Go-based email notification service for MoneyLane. Brevo. Postgres. Idempotent.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/notifications/email` | Send notification (idempotent via event_id) |
| GET | `/notifications/health` | Health check |

## API

### Send Notification

```bash
curl -X POST http://localhost:8080/notifications/email \
  -H "Content-Type: application/json" \
  -d '{"event_id":"uuid-123","event_type":"WAITLIST_JOINED","email":"user@gmail.com","metadata":{"name":"Kaushik"}}'
```

**Responses:**
- `{"status":"sent"}` — email delivered
- `{"status":"already_processed"}` — duplicate event_id
- `{"status":"failed"}` — send failed after retries

## Local Development

```bash
# From services/notification/
cp .env.example .env
# Edit .env with your values

# Run (requires Postgres running)
go run ./cmd/server/
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | — | Postgres connection string |
| `BREVO_API_KEY` | Yes | — | Brevo API key |
| `PORT` | No | `8080` | Server port |
| `FROM_EMAIL` | No | `noreply@elevenxstudios.com` | Sender email |

## Tests

```bash
go test ./...
```

## Deployment

Deployed automatically to Cloud Run on push to `master` when files in `services/notification/` change. See `.github/workflows/cd-notification.yml`.
