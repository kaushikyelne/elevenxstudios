package com.moneylane.modules.profile.application.port.in;

import com.moneylane.modules.profile.domain.ProfilePreferences;
import com.moneylane.modules.profile.domain.UserProfile;
import com.moneylane.shared.kernel.UserId;

public interface UpdateMyProfileUseCase {
    UserProfile updateProfile(UserId userId, String displayName, String avatarUrl, ProfilePreferences preferences);
}
