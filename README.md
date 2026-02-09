# MoneyLane

Simple Spring Boot 3.3 project structure with modular monolith and hexagonal architecture.

## Architecture

- **Monorepo**: All modules in a single repository.
- **Modular Monolith**: Feature-based modules (Auth, Profile, Transaction, Budget, Insight).
- **Hexagonal Architecture**: Strict separation of concerns using Ports & Adapters.
  - `domain`: Core business logic and entities (immutable).
  - `application`: Use cases and orchestration (Inbound/Outbound Ports).
  - `infrastructure`: Technical implementations (Persistence, Security, External APIs).
  - `api`: REST Controllers and DTOs.
14: 
15: ## Design Principles
16: 
17: - **Microservice-Ready**: Each module is designed to be easily extracted into a standalone service.
18: - **Shared Kernel**: Common domain primitives (like `UserId`) are shared across modules to ensure consistency without coupling feature logic.
19: - **Isolation**: Cross-module communication happens through defined ports or shared contracts.

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

## Getting Started

### Prerequisites
- JDK 21
- Docker (for PostgreSQL)
- Supabase Project (for `auth-supabase`)

### Configuration
For Supabase integration, provide the following environment variables in a `.env` file in the root directory:

```env
SUPABASE_AUTH_BASE_URL="https://your-project.supabase.co/auth/v1"
SUPABASE_ANON_KEY="your-anon-key"
SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
SUPABASE_ISSUER_URI="https://your-project.supabase.co/auth/v1"
DB_URL="jdbc:postgresql://localhost:5432/your-db"
DB_USERNAME="your-username"
DB_PASSWORD="your-password"
```

The application will automatically load these from the `.env` file during `bootRun`.

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

#### Get Current User Info
**GET** `/api/v1/auth/me`
*Requires standard Supabase JWT in the `Authorization: Bearer <token>` header.*
Synchronizes the user profile with the local database and returns the current user context.

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

## Documentation
- **Swagger UI**: [http://localhost:8080/swagger-ui/index.html](http://localhost:8080/swagger-ui/index.html)
- **Latest Implementation Documentation**: [Profile Walkthrough](.gemini/antigravity/brain/8a5bc8c8-4baa-4f97-a652-43fa78496c84/walkthrough.md)
