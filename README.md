# MoneyLane

Simple Spring Boot 3.x project structure with modular monolith and hexagonal architecture.

## Folder Structure

```
moneylane/
├── bootstrap/
│   ├── build.gradle.kts
│   └── src/main/java/com/moneylane/
│       └── MoneyLaneApplication.java
│
├── modules/
│   ├── transaction/
│   │   ├── build.gradle.kts
│   │   ├── api/
│   │   │   └── src/main/java/com/moneylane/modules/transaction/api/
│   │   │       └── TransactionController.java
│   │   ├── application/
│   │   │   └── src/main/java/com/moneylane/modules/transaction/application/
│   │   │       ├── port/
│   │   │       │   ├── in/
│   │   │       │   │   └── CreateTransactionUseCase.java
│   │   │       │   └── out/
│   │   │       │       └── TransactionRepository.java
│   │   │       └── service/
│   │   │           └── TransactionService.java
│   │   ├── domain/
│   │   │   └── src/main/java/com/moneylane/modules/transaction/domain/
│   │   │       └── Transaction.java
│   │   └── infrastructure/
│   │       └── src/main/java/com/moneylane/modules/transaction/infrastructure/
│   │           └── TransactionRepositoryAdapter.java
│   │
│   ├── budget/
│   │   └── build.gradle.kts
│   │
│   └── insight/
│       └── build.gradle.kts
│
├── shared/
│   ├── kernel/
│   │   ├── build.gradle.kts
│   │   └── src/main/java/com/moneylane/shared/kernel/
│   │       └── EntityId.java
│   │
│   └── contracts/
│       ├── build.gradle.kts
│       └── src/main/java/com/moneylane/shared/contracts/
│           └── TransactionRequest.java
│
├── common/
│   ├── exception/
│   │   ├── build.gradle.kts
│   │   └── src/main/java/com/moneylane/common/exception/
│   │       └── GlobalExceptionHandler.java
│   │
│   └── util/
│       ├── build.gradle.kts
│       └── src/main/java/com/moneylane/common/util/
│           └── ValidationUtils.java
│
├── build.gradle.kts
└── settings.gradle.kts
```

## Architecture

- **Monorepo**: All modules in single repository
- **Modular Monolith**: Feature-based modules
- **Hexagonal Architecture**: Ports & Adapters pattern

## Tech Stack

- Java 21
- Spring Boot 3.3.0
- Gradle (Kotlin DSL)
