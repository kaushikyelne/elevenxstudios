# Implementation Plan: User Profile Module

## STEP 0 — CORE PRIMITIVE ALIGNMENT
Move `UserId` from `auth-common` to `shared:kernel` to ensure clean boundaries.
- [MODIFY] `shared/kernel/src/main/java/com/moneylane/shared/kernel/UserId.java` [NEW]
- [DELETE] `modules/auth/auth-common/domain/src/main/java/com/moneylane/modules/auth/common/domain/UserId.java`
- [MODIFY] Update all imports in `auth` module.

## STEP 1 — MODULE SETUP
Register the new `profile` module.
- [MODIFY] `settings.gradle.kts`
- [MODIFY] `bootstrap/build.gradle.kts`
- [NEW] `modules/profile/build.gradle.kts`

## STEP 2 — DOMAIN LAYER (PURE)
Create pure domain entities without Spring/JPA annotations.
- `UserProfile`: Aggregates profile data.
- `ProfilePreferences`: Value object for theme/notifications.

## STEP 3 — APPLICATION LAYER (USE CASES)
Implement lazy profile creation and strict update logic.
- `GetMyProfileUseCase`, `UpdateMyProfileUseCase` (Inbound Ports)
- `UserProfilePort` (Outbound Port)
- `UserProfileService`: Orchestration and domain-specific exceptions.

## STEP 4 — INFRASTRUCTURE LAYER
JPA implementations and mapping logic.
- `JpaUserProfileEntity`, `JpaUserProfileRepository`
- `JpaUserProfileMapper`
- `JpaUserProfileAdapter`

## STEP 5 — API LAYER
REST Controller using existing `SecurityContext`.
- `ProfileController`: `GET /PATCH /api/v1/profile/me`.

## STEP 6 — DATABASE MIGRATION
- `V5__create_user_profiles.sql`.

## STEP 7 — VERIFICATION
Manual testing via Docker Compose and Swagger UI.
