package com.moneylane.modules.profile.application.service;

import com.moneylane.modules.profile.application.port.out.UserProfilePort;
import com.moneylane.modules.profile.domain.ProfilePreferences;
import com.moneylane.modules.profile.domain.UserProfile;
import com.moneylane.shared.kernel.UserId;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

import java.time.Instant;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

class UserProfileServiceTest {

    private UserProfilePort userProfilePort;
    private UserProfileService userProfileService;

    @BeforeEach
    void setUp() {
        userProfilePort = mock(UserProfilePort.class);
        userProfileService = new UserProfileService(userProfilePort);
    }

    @Test
    void shouldCreateDefaultProfileWhenNotFound() {
        // Given
        UserId userId = new UserId(UUID.randomUUID());
        when(userProfilePort.findByUserId(userId)).thenReturn(Optional.empty());
        when(userProfilePort.save(any(UserProfile.class))).thenAnswer(i -> i.getArguments()[0]);

        // When
        UserProfile profile = userProfileService.getProfile(userId);

        // Then
        assertNotNull(profile);
        assertEquals(userId, profile.getUserId());
        assertTrue(profile.getDisplayName().startsWith("User_"));
        verify(userProfilePort).save(any(UserProfile.class));
    }

    @Test
    void shouldUpdateExistingProfile() {
        // Given
        UserId userId = new UserId(UUID.randomUUID());
        UserProfile existingProfile = UserProfile.builder()
                .userId(userId)
                .displayName("Old Name")
                .preferences(ProfilePreferences.defaultPreferences())
                .createdAt(Instant.now())
                .build();

        when(userProfilePort.findByUserId(userId)).thenReturn(Optional.of(existingProfile));
        when(userProfilePort.save(any(UserProfile.class))).thenAnswer(i -> i.getArguments()[0]);

        ProfilePreferences newPrefs = new ProfilePreferences("dark", true);

        // When
        UserProfile updated = userProfileService.updateProfile(userId, "New Name", "http://avatar.com", newPrefs);

        // Then
        assertEquals("New Name", updated.getDisplayName());
        assertEquals("http://avatar.com", updated.getAvatarUrl());
        assertEquals(newPrefs, updated.getPreferences());
        verify(userProfilePort).save(existingProfile);
    }
}
