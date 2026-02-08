package com.moneylane.modules.profile.application.port.out;

import com.moneylane.modules.profile.domain.UserProfile;
import com.moneylane.shared.kernel.UserId;

import java.util.Optional;

public interface UserProfilePort {
    Optional<UserProfile> findByUserId(UserId userId);

    UserProfile save(UserProfile profile);
}
