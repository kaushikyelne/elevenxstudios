package com.moneylane.modules.auth.common.application.port.out;

import java.util.Optional;

public interface ExternalIdentityProviderPort {
    Optional<ExternalUserContext> getDetailedUser(String externalUserId);

    Optional<ExternalAuthenticationResult> authenticate(String email, String password);
}
