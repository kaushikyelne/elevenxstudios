package com.moneylane.modules.profile.domain;

import lombok.Value;

@Value
public class ProfilePreferences {
    String theme;
    boolean notificationsEnabled;

    public static ProfilePreferences defaultPreferences() {
        return new ProfilePreferences("light", true);
    }
}
