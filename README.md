# 🏦 MoneyLane

**The Proactive Financial Co-pilot.** MoneyLane transforms traditional expense tracking (reactive) into AI-driven guidance (proactive) using real-time interventions, loss-framed predictions, and automated behavior-change loops.

[![Live API](https://img.shields.io/badge/Live%20API-api.moneylane.elevenxstudios.com-blue?style=for-the-badge&logo=google-cloud)](https://api.moneylane.elevenxstudios.com)
[![Java](https://img.shields.io/badge/Java-21-orange?style=for-the-badge&logo=openjdk)](https://www.oracle.com/java/technologies/downloads/#java21)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Go](https://img.shields.io/badge/Go-1.22-00ADD8?style=for-the-badge&logo=go)](https://go.dev/)

---

## 📋 Table of Contents

- [✨ Features at a Glance](#-features-at-a-glance)
- [🏗️ Architecture Overview](#️-architecture-overview)
- [🔧 Tech Stack](#-tech-stack)
- [📂 Project Structure](#-project-structure)
- [🧩 Services & Modules](#-services--modules)
- [📐 High-Level Design](#-high-level-design)
- [📏 Low-Level Design](#-low-level-design)
- [🚀 Getting Started](#-getting-started)
- [📡 API Reference](#-api-reference)
- [🗄️ Database Migrations](#️-database-migrations)
- [🧪 Testing](#-testing)
- [⚙️ CI/CD](#️-cicd)
- [☁️ Cloud Infrastructure](#️-cloud-infrastructure)
- [🛠️ Development Workflow](#️-development-workflow)
- [📚 Documentation](#-documentation)

---

## ✨ Features at a Glance

- **Proactive Interventions**: 3-check pipeline (Soft-block → Daily Limit → Predictive Warning).
- **AI Co-pilot**: Gemini-powered conversational agent for autonomous actions.
- **Loss-Framed Insights**: "You'll WASTE ₹2,400" vs "You'll overspend ₹2,400".
- **Multi-Auth**: Native JWT + Supabase integration.
- **Exactly-Once Notifications**: High-performance Go service for transactional emails.
- **Microservice-Ready**: Modular monolith transitionable to full microservices.

---

## 🏗️ Architecture Overview

The system uses a **polyglot monorepo** approach, balancing the robustness of Java for core identity with the rapid iteration of Python for AI/Financial logic and Go for high-performance delivery.

### System Topology

```mermaid
graph TB
    subgraph "Client Layer"
        MOB[Mobile App]
        WEB[Web App]
    end

    subgraph "GCP Cloud Run"
        subgraph "Java Monolith :8080"
            AUTH[Auth Module]
            PROF[Profile Module]
        end

        subgraph "Python Services"
            FIN[Financial Service :8082]
            AGT[Agent Service :8083]
            WL[Waitlist Service]
        end

        subgraph "Go Service"
            NOTIF[Notification Service :8081]
        end
    end

    subgraph "External"
        SUPA[Supabase Auth]
        GEMINI[Google Gemini 2.0 Flash]
        BREVO[Brevo / Sendinblue]
    end

    subgraph "Data"
        PG[(PostgreSQL / Cloud SQL)]
    end

    MOB --> AUTH
    MOB --> FIN
    MOB --> AGT
    WEB --> WL

    AUTH --> SUPA
    AUTH --> PG
    PROF --> PG
    FIN --> PG
    FIN -->|fire alert| NOTIF
    AGT -->|tool calls| FIN
    AGT --> GEMINI
    NOTIF --> BREVO
    NOTIF --> PG
    WL --> PG
    WL -->|fire-and-forget| NOTIF
```

| Service | Tech | Role | Port |
|---------|------|------|------|
| **Java Monolith** | Java 21 / Spring Boot | Identity (Auth + Supabase) & Profile management | 8080 |
| **Financial Service** | Python / FastAPI / SQLModel | Core data engine: transactions, budgets, insight engine, **intervention engine**, predictions | 8082 |
| **Agent Service** | Python / FastAPI / Gemini | AI co-pilot: conversational interface with tool-calling for autonomous actions | 8083 |
| **Notification Service** | Go / net/http / Brevo | Exactly-once transactional email delivery with idempotency | 8081 |
| **Waitlist Service** | Python / FastAPI / SQLAlchemy | Pre-launch email collection | — |

---

## 🔧 Tech Stack

- **Backend**: Java 21, Spring Boot 3.3, Gradle 8.10
- **AI/Financial**: Python 3.11-3.12, FastAPI, SQLModel, Gemini 2.0 Flash
- **Messaging**: Go 1.22, Brevo REST API
- **Persistence**: PostgreSQL, Flyway, Alembic
- **Platform**: GCP Cloud Run, Cloud SQL, Secret Manager, Workload Identity

---

## 📂 Project Structure

```
moneylane/
├── bootstrap/          # Spring Boot Application runner & configuration
├── modules/            # Java Modular Monolith
│   ├── auth/           # Multi-module Authentication (local/supabase)
│   ├── profile/        # User Profile management
│   ├── transaction*    # (Java scaffold - logic moved to Python)
│   └── budget/         # (Java scaffold)
├── services/           # Standalone Microservices
│   ├── financial-service/ # Core Data & Intervention Engine (Python)
│   ├── agent-service/     # AI Co-pilot (Python/Gemini)
│   ├── notification/      # Email delivery service (Go)
│   └── waitlist/          # Waitlist microservice (Python)
├── shared/
│   ├── kernel/         # Core domain primitives (UserId, etc.)
│   └── contracts/      # Cross-module communication contracts
└── common/             # Global utilities and exception handling
```

---

## 🧩 Services & Modules

<details>
<summary><b>🔐 Java Monolith: Auth & Profile</b></summary>

- **Auth Module**: Supports native BCrypt+JWT and Supabase 3rd party providers.
- **Profile Module**: Decoupled self-service management. Uses JSONB for flexible preferences.
- **Hexagonal Architecture**: Strict split into `domain`, `application`, `infrastructure`, and `api`.
</details>

<details>
<summary><b>🧠 Financial Service (The Brain)</b></summary>

- **Predictor**: Real-time spending pace projection.
- **Intervention Engine**: 3-check pipeline (Soft-block → Daily Limit → Predictive Warning).
- **Ranking**: Actionability-weighted insight scoring (`Impact × 0.6 + Actionability × 0.4`).
</details>

<details>
<summary><b>🤖 Agent Service (Co-pilot)</b></summary>

- **Persona**: Action-first co-pilot using loss-framing.
- **Tools**: Autonomous execution via `apply_action()` on backend.
- **Engine**: Google Gemini 2.0 Flash.
</details>

<details>
<summary><b>📧 Notification Service (Go)</b></summary>

- **Reliability**: Exactly-once delivery using `INSERT-first` idempotency.
- **Performance**: High-concurrency Go implementation with exponential backoff retries.
</details>

---

## 📐 High-Level Design

### Data Architecture
All services share a single **Cloud SQL PostgreSQL** instance, isolated by table/schema ownership:
- **Flyway**: Manages Java schemas (`users`, `user_profiles`).
- **SQLModel**: Manages Financial engine tables.
- **Alembic**: Manages Waitlist service.

### Communication Patterns
- **Agent → Financial**: Synchronous REST for data/actions.
- **Financial → Notification**: Async fire-and-forget for critical alerts.
- **Client → Java**: JWT-protected REST.

### Authentication Flow
1. **Local**: Register → Store Hash → Issue JWT.
2. **Supabase**: Validate Externally → Sync User Record → Issue Mirror JWT if needed.

---

## 📏 Low-Level Design

<details>
<summary><b>Java Hexagonal Detail</b></summary>

| Component | Layer | Purpose |
|-----------|-------|---------|
| `auth-common` | Domain/Ports | Shared `User` entity & persistence interfaces |
| `auth-local` | Infrastructure | JWT signing, BCrypt, JPA Adapters |
| `profile` | Application | Lazy profile creation, self-service logic |

</details>

<details>
<summary><b>Financial Engine (Python)</b></summary>

- **Transaction Path**: Log → Categorize → Update Budget → Trigger Intervention Pipeline.
- **Insight Detecting**:
  - Overspending: `spent > limit`
  - Waste: e.g., Late-night Swiggy orders > ₹500.
  - Behavior: Recurring weekday Uber rides > 9 PM.
</details>

<details>
<summary><b>Notification Reliability (Go)</b></summary>

The service ensures exactly-once delivery via a PostgreSQL-backed idempotency table.
1. `POST` request with `event_id`.
2. Attempt `INSERT` into `notifications`.
3. If unique constraint fails → `200 Already Processed`.
4. If success → Dispatch to Brevo + Update status.

</details>

---

## 🚀 Getting Started

### Prerequisites
- JDK 21
- Docker (for local PG)
- Supabase Project (for `auth-supabase`)

### Configuration
Create a `.env` in the root:
```env
SUPABASE_AUTH_BASE_URL=https://xyz.supabase.co/auth/v1
SUPABASE_ANON_KEY=your-key
DB_URL=jdbc:postgresql://localhost:5432/moneylane
DB_USERNAME=postgres
DB_PASSWORD=password
```

### Running Locally
```bash
# Start DB
docker-compose up -d db

# Run Monolith
./gradlew :bootstrap:bootRun

# Run Python Services (example)
cd services/financial-service && uvicorn app.main:app --port 8082
```

---

## 📡 API Reference

| Service | Base URL | Docs |
|---------|----------|------|
| **Core API** | `https://api.moneylane.elevenxstudios.com` | [/swagger-ui/index.html](https://api.moneylane.elevenxstudios.com/swagger-ui/index.html) |
| **Financial** | `:8082` | `/docs` (FastAPI Swagger) |
| **Agent** | `:8083` | `/docs` |

---

## 🧪 Testing

```bash
# Run all Java tests
./gradlew test

# Run Python tests (Financial Service)
cd services/financial-service && pytest
```

---

## ⚙️ CI/CD

Merges to `master` trigger automated deployments to **GCP Cloud Run**.

- **Global CI**: Tests both Java and Python services on every PR.
- **CD Pipeline**: OIDC via Workload Identity (passwordless).
- **Security**: Database credentials managed via GCP Secret Manager.

---

## ☁️ Cloud Infrastructure

- **Compute**: GCP Cloud Run (Serverless auto-scaling).
- **Database**: GCP Cloud SQL (PostgreSQL with Private IP).
- **Secrets**: GCP Secret Manager.
- **SSL**: Automatic provisioning via Google.

---

## 🛠️ Development Workflow

1.  **Add Module**: Create in `modules/`, register in `settings.gradle.kts`.
2.  **Hexagonal**: `domain` → `application` → `infrastructure` → `api`.
3.  **Migrations**: Add `.sql` file to `db/migration` in the relevant module.

---

## 📊 Module Status

| Component | Status | Tech |
|-----------|--------|------|
| **Auth** | ✅ Done | Java |
| **Profile** | ✅ Done | Java |
| **Financial** | ✅ Done | Python |
| **Agent** | ✅ Done | Python |
| **Notification** | ✅ Done | Go |
| **Waitlist** | ✅ Done | Python |

---

## 📚 Documentation

- [Profile Implementation Plan](docs/profile-implementation-plan.md)
- [Profile Walkthrough](docs/profile-walkthrough.md)

---
Developed with ❤️ by **elevenxstudios**.
