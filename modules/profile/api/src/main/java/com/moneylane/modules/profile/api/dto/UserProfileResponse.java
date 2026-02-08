package com.moneylane.modules.profile.api.dto;

import com.moneylane.modules.profile.domain.UserProfile;
import io.swagger.v3.oas.annotations.media.Schema;
import java.util.UUID;

@Schema(description = "User profile response. Contains both immutable identity fields and mutable profile data.")
public record UserProfileResponse(
                @Schema(description = "User's unique identifier (immutable)", example = "a7ca2919-19a3-4b54-ab5d-5755c00049db", accessMode = Schema.AccessMode.READ_ONLY) UUID userId,

                @Schema(description = "User's display name (mutable)", example = "Kaushik") String displayName,

                @Schema(description = "URL to user's avatar image (mutable)", example = "https://example.com/avatar.png", nullable = true) String avatarUrl,

                @Schema(description = "User preferences (mutable)") PreferencesDto preferences) {

        public static UserProfileResponse fromDomain(UserProfile profile) {
                return new UserProfileResponse(
                                profile.getUserId().getValue(),
                                profile.getDisplayName(),
                                profile.getAvatarUrl(),
                                new PreferencesDto(
                                                profile.getPreferences().getTheme(),
                                                profile.getPreferences().isNotificationsEnabled()));
        }

        @Schema(description = "User preferences")
        public record PreferencesDto(
                        @Schema(description = "UI theme preference", example = "dark", allowableValues = {
                                        "light", "dark" }) String theme,

                        @Schema(description = "Whether notifications are enabled", example = "true") boolean notificationsEnabled) {
        }
}
