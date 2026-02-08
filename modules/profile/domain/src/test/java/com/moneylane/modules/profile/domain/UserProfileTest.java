package com.moneylane.modules.profile.domain;

import com.moneylane.shared.kernel.UserId;
import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

class UserProfileTest {

    @Test
    void shouldUpdateProfileCorrectly() {
        // Given
        UserId userId = new UserId(UUID.randomUUID());
        UserProfile profile = UserProfile.builder()
                .userId(userId)
                .displayName("Old Name")
                .avatarUrl("old-url")
                .preferences(ProfilePreferences.defaultPreferences())
                .createdAt(Instant.now())
                .updatedAt(Instant.now())
                .build();

        ProfilePreferences newPrefs = new ProfilePreferences("dark", false);

        // When
        profile.update("New Name", "new-url", newPrefs);

        // Then
        assertEquals("New Name", profile.getDisplayName());
        assertEquals("new-url", profile.getAvatarUrl());
        assertEquals(newPrefs, profile.getPreferences());
        assertNotNull(profile.getUpdatedAt());
    }
}
