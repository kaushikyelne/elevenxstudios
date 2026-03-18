# Agent Service

AI-powered financial assistant for MoneyLane, built with **FastAPI** and **Google Gemini**.

## 🏗 Architecture

The service acts as an orchestration layer for AI agents. It uses the Google Gemini 2.0 Flash model to provide financial insights and eventually interact with other services via tools.

## 🚀 Features

- **FastAPI**: Async performance for LLM streaming and concurrency.
- **Google Gemini**: State-of-the-art multimodal LLM integration.
- **Cloud Run**: Fully managed serverless deployment on GCP.
- **Secret Manager**: Secure handling of API keys.

## 🚥 Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/v1/agent/chat` | OIDC | Interact with the financial agent |
| `GET` | `/api/v1/agent/health` | Public | Service health check |

### Health Check
**GET** `/api/v1/agent/health`
Response: `{"status": "ok"}`

## 🛠 Local Development

### Prerequisites
- Python 3.12+
- Gemini API Key

### Setup
```bash
# 1. Prepare environment
cd services/agent-service
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env
cp .env.example .env
# Add GEMINI_API_KEY=your_key

# 4. Run service
uvicorn app.main:app --reload --port 8001
```

## 🔧 Infrastructure & Deployment

### Environment Variables
| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google AI Studio API Key (Stored in Secret Manager) |
| `PORT` | Listening port (Default: 8080) |

### GCP Cloud Run
Deployed automatically via GitHub Actions on push to `master`. 
- **Service Account**: Needs `Secret Manager Secret Accessor` for `gemini-api-key`.
- **Resources**: 1 CPU, 512Mi Memory.
