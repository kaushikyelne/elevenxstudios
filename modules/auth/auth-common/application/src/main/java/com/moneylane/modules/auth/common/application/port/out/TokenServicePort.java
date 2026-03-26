package com.moneylane.modules.auth.common.application.port.out;

import java.time.Instant;

public interface TokenServicePort {
    TokenResult generateAccessToken(String email);

    TokenResult generateRefreshToken(String email);

    TokenValidationResult validateAccessToken(String token);

    TokenValidationResult validateRefreshToken(String token);

    record TokenResult(String token, Instant expiresAt) {
    }

    record TokenValidationResult(boolean isValid, String email) {
    }
}
