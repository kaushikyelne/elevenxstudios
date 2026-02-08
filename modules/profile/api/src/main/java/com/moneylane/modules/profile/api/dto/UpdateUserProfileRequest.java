package com.moneylane.modules.profile.api.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Size;

@Schema(description = "Request to update user profile. All fields are optional — only provided fields will be updated.")
public record UpdateUserProfileRequest(
                @Schema(description = "New display name (mutable)", example = "Kaushik", maxLength = 100) @Size(max = 100) String displayName,

                @Schema(description = "New avatar URL (mutable)", example = "https://example.com/avatar.png", maxLength = 255) @Size(max = 255) String avatarUrl,

                @Schema(description = "Preference updates (mutable)") PreferencesRequest preferences) {

        @Schema(description = "Preference update fields")
        public record PreferencesRequest(
                        @Schema(description = "UI theme preference", example = "dark", allowableValues = {
                                        "light", "dark" }) String theme,

                        @Schema(description = "Enable or disable notifications", example = "true") Boolean notificationsEnabled) {
        }
}
