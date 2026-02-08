package com.moneylane.modules.profile.api;

import com.moneylane.modules.profile.api.dto.UpdateUserProfileRequest;
import com.moneylane.modules.profile.api.dto.UserProfileResponse;
import com.moneylane.modules.profile.application.port.in.GetMyProfileUseCase;
import com.moneylane.modules.profile.application.port.in.UpdateMyProfileUseCase;
import com.moneylane.modules.profile.domain.ProfilePreferences;
import com.moneylane.modules.profile.domain.UserProfile;
import com.moneylane.shared.kernel.UserId;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/api/v1/profile")
@RequiredArgsConstructor
@Tag(name = "User Profile", description = "Self-service profile management. All endpoints operate on the **authenticated user's own profile only** — there is no way to view or modify other users' profiles.")
@SecurityRequirement(name = "bearerAuth")
public class ProfileController {

    private final GetMyProfileUseCase getMyProfileUseCase;
    private final UpdateMyProfileUseCase updateMyProfileUseCase;

    @GetMapping("/me")
    @Operation(summary = "Get my profile", description = """
            Returns the authenticated user's profile. If no profile exists, one is **automatically created** with default values:
            - `displayName`: Generated from user ID prefix
            - `preferences.theme`: "light"
            - `preferences.notificationsEnabled`: true

            **Immutable fields** (cannot be changed via API):
            - `userId` — derived from JWT, never modifiable
            - `createdAt` — set once on creation
            """)
    @ApiResponse(responseCode = "200", description = "Profile retrieved successfully")
    @ApiResponse(responseCode = "401", description = "Missing or invalid JWT")
    public ResponseEntity<UserProfileResponse> getMyProfile() {
        UserId userId = getCurrentUserId();
        UserProfile profile = getMyProfileUseCase.getProfile(userId);
        return ResponseEntity.ok(UserProfileResponse.fromDomain(profile));
    }

    @PatchMapping("/me")
    @Operation(summary = "Update my profile", description = """
            Partially updates the authenticated user's profile. Only provided fields are updated; omitted fields remain unchanged.

            **Mutable fields:**
            - `displayName` — user's display name (max 100 chars)
            - `avatarUrl` — URL to avatar image (max 255 chars)
            - `preferences.theme` — UI theme preference
            - `preferences.notificationsEnabled` — notification toggle

            **Immutable fields (ignored if sent):**
            - `userId` — cannot be changed
            - `createdAt` — cannot be changed
            """)
    @ApiResponse(responseCode = "200", description = "Profile updated successfully")
    @ApiResponse(responseCode = "401", description = "Missing or invalid JWT")
    public ResponseEntity<UserProfileResponse> updateMyProfile(@RequestBody UpdateUserProfileRequest request) {
        UserId userId = getCurrentUserId();

        UserProfile current = getMyProfileUseCase.getProfile(userId);

        String newDisplayName = request.displayName() != null ? request.displayName() : current.getDisplayName();
        String newAvatarUrl = request.avatarUrl() != null ? request.avatarUrl() : current.getAvatarUrl();

        ProfilePreferences newPrefs = current.getPreferences();
        if (request.preferences() != null) {
            newPrefs = new ProfilePreferences(
                    request.preferences().theme() != null ? request.preferences().theme()
                            : current.getPreferences().getTheme(),
                    request.preferences().notificationsEnabled() != null ? request.preferences().notificationsEnabled()
                            : current.getPreferences().isNotificationsEnabled());
        }

        UserProfile updated = updateMyProfileUseCase.updateProfile(userId, newDisplayName, newAvatarUrl, newPrefs);
        return ResponseEntity.ok(UserProfileResponse.fromDomain(updated));
    }

    private UserId getCurrentUserId() {
        Object principal = SecurityContextHolder.getContext().getAuthentication().getPrincipal();

        if (principal instanceof Jwt jwt) {
            return new UserId(UUID.fromString(jwt.getSubject()));
        }

        if (principal instanceof String principalString) {
            return new UserId(UUID.fromString(principalString));
        }

        throw new IllegalStateException("Unexpected principal type: " + principal.getClass());
    }
}
