package com.moneylane.modules.auth.application.port.out;

import java.time.Instant;

public interface TokenServicePort {
    TokenResult generateAccessToken(String email, String role);

    TokenResult generateRefreshToken(String email);

    TokenValidationResult validateAccessToken(String token);

    TokenValidationResult validateRefreshToken(String token);

    record TokenResult(String token, Instant expiresAt) {
    }

    record TokenValidationResult(boolean isValid, String email, String role) {
    }
}
