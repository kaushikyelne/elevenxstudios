package com.moneylane.modules.auth.common.application.port.out;

import java.util.Optional;

public interface ExternalIdentityProviderPort {
    Optional<ExternalUserContext> getDetailedUser(String externalId);
}
