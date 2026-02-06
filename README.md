# MoneyLane

Simple Spring Boot 3.3 project structure with modular monolith and hexagonal architecture.

## Architecture

- **Monorepo**: All modules in a single repository.
- **Modular Monolith**: Feature-based modules (Auth, Transaction, Budget, Insight).
- **Hexagonal Architecture**: Strict separation of concerns using Ports & Adapters.
  - `domain`: Core business logic and entities (immutable).
  - `application`: Use cases and orchestration (Inbound/Outbound Ports).
  - `infrastructure`: Technical implementations (Persistence, Security, External APIs).
  - `api`: REST Controllers and DTOs.

## Tech Stack

- **Java**: 21 (configured for 20 in some environments)
- **Spring Boot**: 3.3.0
- **Gradle**: 9.3.1 (Kotlin DSL)
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
│   ├── transaction/    # Transaction management
│   ├── budget/         # Budgeting logic
│   └── insight/        # Analytics and reports
├── shared/
│   ├── kernel/         # Core domain primitives (EntityId, etc.)
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

## Getting Started

### Prerequisites
- JDK 21
- Docker (for PostgreSQL)
- Supabase Project (for `auth-supabase`)

### Configuration
For Supabase integration, update your `application.yml`:
```yaml
supabase:
  jwt:
    secret: "YOUR_JWT_SECRET"
    issuer: "https://YOUR_PROJECT.supabase.co/auth/v1"
```

### Running the App
```bash
./gradlew :bootstrap:bootRun
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

#### Get Current User Info
**GET** `/api/v1/auth/supabase/me`
*Requires standard Supabase JWT in the `Authorization: Bearer <token>` header.*

**Response**:
```json
{
  "id": "supabase-uuid",
  "email": "user@example.com",
  "claims": { ... }
}
```

## Documentation
- **Swagger UI**: [http://localhost:8080/swagger-ui/index.html](http://localhost:8080/swagger-ui/index.html)
- **Architecture Walkthrough**: [walkthrough.md](.gemini/antigravity/brain/f95c4d7a-fc15-4a80-a446-c815847811ce/walkthrough.md)
