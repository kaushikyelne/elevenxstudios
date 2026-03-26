package com.moneylane.modules.auth.common.application.port.out;

import java.util.Optional;

public record ExternalAuthenticationResult(
        String accessToken,
        String refreshToken,
        long expiresIn,
        ExternalUserContext userContext) {
}
