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
│   ├── auth/           # User Registration & Authentication
│   ├── transaction/    # Transaction management
│   ├── budget/         # Budgeting logic
│   └── insight/        # Analytics and reports
├── shared/
│   ├── kernel/         # Core domain primitives (EntityId, etc.)
│   └── contracts/      # Cross-module communication contracts
└── common/             # Utilities and global exception handling
```

## Features

### Auth Module
- **User Registration**: Secure registration with BCrypt password hashing.
- **Validation**: Strict email format and password length validation.
- **Hexagonal Flow**:
  1. `AuthController` receives request.
  2. `RegisterUserUseCase` (Port) is called.
  3. `AuthService` executes business logic.
  4. `PasswordEncoderPort` is used for hashing.
  5. `UserRepository` (Port) saves to DB.

## Getting Started

### Prerequisites
- JDK 20 or 21
- Docker (for PostgreSQL)

### Running the App
```bash
./gradlew :bootstrap:bootRun
```

### API Usage - User Registration
**POST** `/api/v1/auth/register`

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

## Documentation
- **Swagger UI**: [http://localhost:8080/swagger-ui/index.html](http://localhost:8080/swagger-ui/index.html)
