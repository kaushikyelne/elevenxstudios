package com.moneylane.modules.profile.domain;

import com.moneylane.shared.kernel.UserId;
import lombok.Builder;
import lombok.Getter;

import java.time.Instant;

@Getter
@Builder
public class UserProfile {
    private final UserId userId;
    private String displayName;
    private String avatarUrl;
    private ProfilePreferences preferences;
    private final Instant createdAt;
    private Instant updatedAt;

    public void update(String displayName, String avatarUrl, ProfilePreferences preferences) {
        this.displayName = displayName;
        this.avatarUrl = avatarUrl;
        this.preferences = preferences;
        this.updatedAt = Instant.now();
    }
}
