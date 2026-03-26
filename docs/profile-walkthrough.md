# Walkthrough: User Profile Module

## Implementation Complete ✅

The **User Profile** module is now live and verified, following Hexagonal Architecture principles.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/profile/me` | Get current user's profile (auto-creates if not exists) |
| `PATCH` | `/api/v1/profile/me` | Update display name, avatar, or preferences |

## Verification Results

### GET (Lazy Creation)
```json
{
    "userId": "a7ca2919-19a3-4b54-ab5d-5755c00049db",
    "displayName": "User_a7ca2919",
    "avatarUrl": null,
    "preferences": {"theme": "light", "notificationsEnabled": true}
}
```

### PATCH (Update)
```json
{
    "userId": "a7ca2919-19a3-4b54-ab5d-5755c00049db",
    "displayName": "Kaushik",
    "avatarUrl": "https://example.com/avatar.png",
    "preferences": {"theme": "dark", "notificationsEnabled": true}
}
```

## Key Files

| Layer | File |
|-------|------|
| Domain | [UserProfile.java](file:///Users/kaushikyelne/Documents/MyProjects/elevenxstudios/modules/profile/domain/src/main/java/com/moneylane/modules/profile/domain/UserProfile.java) |
| Application | [UserProfileService.java](file:///Users/kaushikyelne/Documents/MyProjects/elevenxstudios/modules/profile/application/src/main/java/com/moneylane/modules/profile/application/service/UserProfileService.java) |
| API | [ProfileController.java](file:///Users/kaushikyelne/Documents/MyProjects/elevenxstudios/modules/profile/api/src/main/java/com/moneylane/modules/profile/api/ProfileController.java) |
| Migration | [V5__create_user_profiles.sql](file:///Users/kaushikyelne/Documents/MyProjects/elevenxstudios/modules/profile/infrastructure/src/main/resources/db/migration/V5__create_user_profiles.sql) |

## Architecture Boundaries Respected

- ✅ Profile module depends only on `UserId` (from `shared:kernel`)
- ✅ No direct Supabase calls
- ✅ No `/users` CRUD or `/profile/{id}` endpoints
- ✅ Pure domain objects (no JPA annotations)
