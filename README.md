# MoneyLane

**The Proactive Financial Co-pilot.** MoneyLane transforms traditional expense tracking (reactive) into AI-driven guidance (proactive) using real-time interventions, loss-framed predictions, and automated behavior-change loops.

🚀 **Live API**: [api.moneylane.elevenxstudios.com](https://api.moneylane.elevenxstudios.com)

## Architecture

- **Monorepo**: All modules in a single repository.
- **Modular Monolith**: Feature-based modules (Auth, Profile, Transaction, Budget, Insight).
- **Hexagonal Architecture**: Strict separation of concerns using Ports & Adapters.
  - `domain`: Core business logic and entities (immutable).
  - `application`: Use cases and orchestration (Inbound/Outbound Ports).
  - `infrastructure`: Technical implementations (Persistence, Security, External APIs).
  - `api`: REST Controllers and DTOs.

## Design Principles

- **Microservice-Ready**: Each module is designed to be easily extracted into a standalone service.
- **Shared Kernel**: Common domain primitives (like `UserId`) are shared across modules to ensure consistency without coupling feature logic.
- **Isolation**: Cross-module communication happens through defined ports or shared contracts.

## Tech Stack

- **Java**: 21
- **Spring Boot**: 3.3.0
- **Gradle**: 8.10 (Kotlin DSL)
- **DB**: PostgreSQL with Flyway migrations
- **Lombok**: Managed via `io.freefair.lombok` plugin

## Folder Structure

```
moneylane/
├── bootstrap/          # Spring Boot Application runner & configuration
├── modules/
│   ├── auth/           # Multi-module Authentication System
│   │   ├── auth-common/  # Shared domain, ports, and common logic
│   │   ├── auth-local/   # Native Username/Password & JWT implementation
│   │   └── auth-supabase/# Supabase 3rd party authentication provider
│   ├── profile/        # User Profile management (self-service)
│   ├── transaction/    # Transaction management
│   ├── budget/         # Budgeting logic
│   └── insight/        # Analytics and reports
├── services/
│   ├── financial-service/ # Core Data & Intervention Engine (Python/FastAPI)
│   └── waitlist/          # Pre-launch waitlist microservice (Python/FastAPI)
├── shared/
│   ├── kernel/         # Core domain primitives (UserId, etc.)
│   └── contracts/      # Cross-module communication contracts
└── common/             # Utilities and global exception handling
```

## Features

### Auth Module (Multi-Provider)
The authentication module follows a multi-module pattern to support both internal and external identity providers.

- **`auth-common`**: Centralizes the shared `User` domain model and outbound ports (`UserRepository`, `TokenServicePort`, `PasswordEncoderPort`).
- **`auth-local`**: 
    - **User Registration**: Secure registration with BCrypt password hashing.
    - **JWT Authentication**: Stateless authentication using access and refresh tokens.
- **`auth-supabase`**:
    - **External Auth**: Seamless integration with Supabase Auth.
    - **Stateless Validation**: Backend JWT validation using Supabase project secrets.
    - **Identity Mapping**: Unified endpoint for current user context.

### Profile Module
Self-service profile management following Hexagonal Architecture. Designed for high isolation; it depends only on `UserId` from `shared:kernel` and is **fully decoupled** from the Auth module's internal database.

- **Lazy Creation**: Profile auto-created on first access with sensible defaults.
- **Self-Only Access**: Users can only view/modify their own profile (`/me` endpoints).
- **JSONB Preferences**: Theme and notification settings stored efficiently.
- **Mutable Fields**: `displayName`, `avatarUrl`, `preferences`
- **Immutable Fields**: `userId`, `createdAt`

## Standalone Services

### Waitlist Service
Minimal FastAPI microservice for pre-launch email collection. Deployed as a standalone Cloud Run service, sharing the same Cloud SQL instance (`waitlist` schema).

- **Stack**: Python 3.12 · FastAPI · SQLAlchemy (async) · asyncpg · Alembic
- **Live**: `https://waitlist-service-972358167214.us-central1.run.app`
- **Docs**: `https://waitlist-service-972358167214.us-central1.run.app/docs`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/waitlist/join` | POST | Submit email to join waitlist (idempotent, case-insensitive dedup) |
| `/api/v1/waitlist/health` | GET | Health check |
| `/api/v1/waitlist/count` | GET | Total signups count |

### Financial Service (The Core Engine)
MoneyLane's "Brain". A high-performance Python service that handles all data writes, budget tracking, and the **Intervention Engine**.

- **Stack**: Python 3.11 · FastAPI · SQLModel · PostgreSQL · httpx
- **Engine**: 
  - **Predictor**: Real-time spending pace projection and month-end overspend forecasting.
  - **Intervention**: 3-check pipeline (Soft-block → Daily Limit → Predictive Warning).
  - **Ranking**: Actionability-weighted insight scoring (Normalized Impact × 0.6 + Actionability × 0.4).
- **Proactive Alerts**: Direct HTTP fire to Notification Service on HIGH/CRITICAL thresholds (no LLM in the critical path).

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/transactions/` | POST | Log transaction + trigger real-time intervention engine |
| `/api/v1/insights/home` | GET | Action-first financial insights |
| `/api/v1/insights/predictions` | GET | Forecasted overspends for all categories |
| `/api/v1/actions/` | POST | Action layer (set-daily-limit, soft-block, feedback) |

### Agent Service
The conversational co-pilot interface for MoneyLane, using **Google Gemini** (Gemini 2.0 Flash).

- **Stack**: Python 3.12 · FastAPI · Google Generative AI SDK
- **Persona**: Action-first co-pilot using loss-framing and autonomous tool usage.
- **Tools**: `apply_action()` (direct execution of backend interventions via Agent API).

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/agent/chat` | POST | Interact with the financial co-pilot |
| `/api/v1/agent/health` | GET | Health check |

#### Join Waitlist
**POST** `/api/v1/waitlist/join`
```json
{"email": "user@example.com"}
```
**Response**:
```json
{"message": "Welcome to the waitlist!", "email": "user@example.com", "created_at": "2026-03-03T10:44:24Z"}
```

## Getting Started

### Prerequisites
- JDK 21
- Docker (for PostgreSQL)
- Supabase Project (for `auth-supabase`)

### Configuration

The application requires specific environment variables to link with Supabase and the database. Create a `.env` file in the root directory:

| Variable | Description | Example |
|----------|-------------|---------|
| `SUPABASE_AUTH_BASE_URL` | Supabase Auth API URL | `https://xyz.supabase.co/auth/v1` |
| `SUPABASE_ANON_KEY` | Public Anon Key | `your-anon-key` |
| `SUPABASE_SERVICE_ROLE_KEY` | Admin Service Role Key | `your-service-role-key` |
| `SUPABASE_ISSUER_URI` | JWT Issuer URL | `https://xyz.supabase.co/auth/v1` |
| `DB_URL` | PostgreSQL JDBC URL | `jdbc:postgresql://localhost:5432/moneylane` |
| `DB_USERNAME` | Database User | `postgres` |
| `DB_PASSWORD` | Database Password | `password` |

The application automatically loads these from the `.env` file during `bootRun` or via `docker-compose`.

### Running the App

#### Locally with Gradle
```bash
./gradlew :bootstrap:bootRun
```

#### With Docker Compose
Ensure you have a `.env` file with the required environment variables.

To start the environment:
```bash
docker-compose up --build
```

To stop and **reset** the database:
```bash
docker-compose down -v
```

## API Usage

### Native Authentication (auth-local)

#### User Registration
**POST** `/api/v1/auth/local/register`

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

#### User Login
**POST** `/api/v1/auth/local/login`

#### Token Refresh
**POST** `/api/v1/auth/local/refresh`

### Supabase Authentication (auth-supabase)

#### User Login
**POST** `/api/v1/auth/login`
Authenticates a user with Supabase using email and password, returning tokens.

#### Get Current User Identity
**GET** `/api/v1/auth/me`
*Requires standard Supabase JWT.*
Verifies the JWT and returns the **Identity Context** (User Account info). This ensures a record exists in the local `users` table for reference by other modules.

**Response**:
```json
{
  "id": "local-uuid",
  "email": "user@example.com",
  "providerUserId": "supabase-uuid",
  "status": "ACTIVE"
}
```

### Profile (profile)

#### Get My Profile
**GET** `/api/v1/profile/me`
*Requires JWT in `Authorization: Bearer <token>` header.*
Returns the authenticated user's profile. Auto-creates if not exists.

**Response**:
```json
{
  "userId": "a7ca2919-19a3-4b54-ab5d-5755c00049db",
  "displayName": "Kaushik",
  "avatarUrl": "https://example.com/avatar.png",
  "preferences": { "theme": "dark", "notificationsEnabled": true }
}
```

#### Update My Profile
**PATCH** `/api/v1/profile/me`
*Partial update — only provided fields are modified.*

```json
{
  "displayName": "New Name",
  "avatarUrl": "https://newurl.com/avatar.png",
  "preferences": { "theme": "dark" }
}
```

## Database Migrations

This project uses **Flyway** for database schema management.
- Migrations are located in: `modules/<module-name>/infrastructure/src/main/resources/db/migration`
- Naming convention: `V<Number>__<Description>.sql` (e.g., `V5__create_user_profiles.sql`)
- Migrations run automatically on application startup.

## Testing

Each module contains its own sets of tests following the hexagonal layers.

- **Unit Tests**: Test core domain logic and application services with mocks.
- **Integration Tests**: Test infrastructure adapters (Persistence/PostgreSQL) using `@DataJpaTest`.
- **Run all tests**:
  ```bash
  ./gradlew test
  ```

## CI/CD

### CI — Continuous Integration
Every pull request to `master` or `develop` triggers an automated build and test pipeline.

- **Workflow**: `.github/workflows/ci.yml`
- **Java**: Checkout → JDK 21 → Gradle (cached) → `./gradlew build`
- **Python**: Matrix build → `pytest` for `financial-service`, `agent-service`, and `waitlist`
- **Test Reports**: Available as downloadable artifacts in GitHub Actions

### CD — Continuous Deployment
Merges to `master` trigger automated deployments to **GCP Cloud Run**.

- **Main API** (`.github/workflows/cd.yml`): Deploys the Java monolith after global CI passes
- **Service CD** (`.github/workflows/cd-*.yml`): Individual service deployments (Financial, Agent, Waitlist) gated by service-specific `pytest` unit tests.

**Shared Infrastructure**:
- **Auth**: Workload Identity Federation (OIDC) — no long-lived credentials
- **Image Registry**: GCP Artifact Registry (tagged with git SHA)
- **Database**: Cloud SQL via proxy, credentials from Secret Manager
- **Health Gate**: Retry-based verification

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `GCP_PROJECT_ID` | Google Cloud project ID |
| `GCP_REGION` | Deployment region (e.g., `us-central1`) |
| `GCP_ARTIFACT_REPO` | Artifact Registry repository name |
| `CLOUD_RUN_SERVICE` | Cloud Run service name |
| `WIF_PROVIDER` | Workload Identity Federation provider |
| `WIF_SERVICE_ACCOUNT` | GCP service account for deployments |
| `DB_URL` | Production database JDBC URL |
| `DB_USERNAME` | Production database username |

> **Note**: `DB_PASSWORD` is managed via GCP Secret Manager (`db-password`), not GitHub Secrets.
>
> The waitlist service uses `waitlist-database-url` in Secret Manager for its `DATABASE_URL`.

### Health Check
```bash
curl https://api.moneylane.elevenxstudios.com/actuator/health
# → {"status":"UP"}
```

## Development Workflow

### Adding a New Module
1. Creating a new folder in `modules/`.
2. Register the module in `settings.gradle.kts`.
3. Add a dependency on the module in `bootstrap/build.gradle.kts` if it's an entry point.
4. Follow Hexagonal Architecture:
   - `domain`: Pure Java objects.
   - `application`: Business use cases and ports.
   - `infrastructure`: Adapters for DB, Security, external APIs.
   - `api`: Controllers and DTOs.

## Troubleshooting

### Docker Connectivity
If the app cannot connect to the database:
- Ensure `.env` has `DB_URL=jdbc:postgresql://db:5432/moneylane` (when running via Docker).
- If running locally: `DB_URL=jdbc:postgresql://localhost:5432/moneylane`.

### Flyway Migration Errors
If migrations fail:
- Reset the database: `docker-compose down -v && docker-compose up`.
- Ensure SQL syntax is compatible with PostgreSQL.

## Documentation
- **Live Swagger UI**: [https://api.moneylane.elevenxstudios.com/swagger-ui/index.html](https://api.moneylane.elevenxstudios.com/swagger-ui/index.html)
- **Local Swagger UI**: [http://localhost:8080/swagger-ui/index.html](http://localhost:8080/swagger-ui/index.html)
- **Design & Implementation Docs**:
  - [High Level & Low Level Design](docs/DESIGN.md)
  - [Profile Implementation Plan](docs/profile-implementation-plan.md)
  - [Profile Walkthrough](docs/profile-walkthrough.md)
  - [Cloud Infrastructure & Deployment](docs/INFRASTRUCTURE.md)
