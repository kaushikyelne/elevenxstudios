package com.moneylane.modules.profile.application.service;

import com.moneylane.modules.profile.application.port.in.GetMyProfileUseCase;
import com.moneylane.modules.profile.application.port.in.UpdateMyProfileUseCase;
import com.moneylane.modules.profile.application.port.out.UserProfilePort;
import com.moneylane.modules.profile.domain.ProfilePreferences;
import com.moneylane.modules.profile.domain.UserProfile;
import com.moneylane.shared.kernel.UserId;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;

@Service
@RequiredArgsConstructor
public class UserProfileService implements GetMyProfileUseCase, UpdateMyProfileUseCase {

    private final UserProfilePort userProfilePort;

    @Override
    @Transactional
    public UserProfile getProfile(UserId userId) {
        return userProfilePort.findByUserId(userId)
                .orElseGet(() -> createDefaultProfile(userId));
    }

    @Override
    @Transactional
    public UserProfile updateProfile(UserId userId, String displayName, String avatarUrl,
            ProfilePreferences preferences) {
        UserProfile profile = getProfile(userId);
        profile.update(displayName, avatarUrl, preferences);
        return userProfilePort.save(profile);
    }

    private UserProfile createDefaultProfile(UserId userId) {
        UserProfile profile = UserProfile.builder()
                .userId(userId)
                .displayName("User_" + userId.getValue().toString().substring(0, 8))
                .preferences(ProfilePreferences.defaultPreferences())
                .createdAt(Instant.now())
                .updatedAt(Instant.now())
                .build();
        return userProfilePort.save(profile);
    }
}
