package com.moneylane.modules.profile.infrastructure.persistence;

import com.moneylane.modules.profile.domain.ProfilePreferences;
import com.moneylane.modules.profile.domain.UserProfile;
import com.moneylane.shared.kernel.UserId;
import org.springframework.stereotype.Component;

import java.util.Map;

@Component
public class JpaUserProfileMapper {

    public JpaUserProfileEntity toEntity(UserProfile profile) {
        return JpaUserProfileEntity.builder()
                .userId(profile.getUserId().getValue())
                .displayName(profile.getDisplayName())
                .avatarUrl(profile.getAvatarUrl())
                .preferences(Map.of(
                        "theme", profile.getPreferences().getTheme(),
                        "notificationsEnabled", profile.getPreferences().isNotificationsEnabled()))
                .createdAt(profile.getCreatedAt())
                .updatedAt(profile.getUpdatedAt())
                .build();
    }

    public UserProfile toDomain(JpaUserProfileEntity entity) {
        Map<String, Object> prefsMap = entity.getPreferences();
        ProfilePreferences preferences = new ProfilePreferences(
                (String) prefsMap.getOrDefault("theme", "light"),
                (Boolean) prefsMap.getOrDefault("notificationsEnabled", true));

        return UserProfile.builder()
                .userId(new UserId(entity.getUserId()))
                .displayName(entity.getDisplayName())
                .avatarUrl(entity.getAvatarUrl())
                .preferences(preferences)
                .createdAt(entity.getCreatedAt())
                .updatedAt(entity.getUpdatedAt())
                .build();
    }
}
