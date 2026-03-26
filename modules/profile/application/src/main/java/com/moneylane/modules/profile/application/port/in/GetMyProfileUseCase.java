package com.moneylane.modules.profile.application.port.in;

import com.moneylane.modules.profile.domain.UserProfile;
import com.moneylane.shared.kernel.UserId;

public interface GetMyProfileUseCase {
    UserProfile getProfile(UserId userId);
}
