package com.moneylane.modules.auth.infrastructure.security;

import com.moneylane.modules.auth.application.port.out.TokenServicePort;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Date;

@Component
public class JwtTokenServiceAdapter implements TokenServicePort {

    private final SecretKey accessKey;
    private final SecretKey refreshKey;
    private final long accessExpirationInSeconds;
    private final long refreshExpirationInSeconds;

    public JwtTokenServiceAdapter(
            @Value("${moneylane.auth.jwt.access-secret:defaultAccessSecretWithMinimumLengthOf32Chars}") String accessSecret,
            @Value("${moneylane.auth.jwt.refresh-secret:defaultRefreshSecretWithMinimumLengthOf32Chars}") String refreshSecret,
            @Value("${moneylane.auth.jwt.access-expiration:3600}") long accessExpirationInSeconds,
            @Value("${moneylane.auth.jwt.refresh-expiration:86400}") long refreshExpirationInSeconds) {
        this.accessKey = Keys.hmacShaKeyFor(accessSecret.getBytes(StandardCharsets.UTF_8));
        this.refreshKey = Keys.hmacShaKeyFor(refreshSecret.getBytes(StandardCharsets.UTF_8));
        this.accessExpirationInSeconds = accessExpirationInSeconds;
        this.refreshExpirationInSeconds = refreshExpirationInSeconds;
    }

    @Override
    public TokenResult generateAccessToken(String email) {
        Instant now = Instant.now();
        Instant expiresAt = now.plus(accessExpirationInSeconds, ChronoUnit.SECONDS);

        String token = Jwts.builder()
                .subject(email)
                .issuedAt(Date.from(now))
                .expiration(Date.from(expiresAt))
                .signWith(accessKey)
                .compact();

        return new TokenResult(token, expiresAt);
    }

    @Override
    public TokenResult generateRefreshToken(String email) {
        Instant now = Instant.now();
        Instant expiresAt = now.plus(refreshExpirationInSeconds, ChronoUnit.SECONDS);

        String token = Jwts.builder()
                .subject(email)
                .issuedAt(Date.from(now))
                .expiration(Date.from(expiresAt))
                .signWith(refreshKey)
                .compact();

        return new TokenResult(token, expiresAt);
    }

    @Override
    public TokenValidationResult validateAccessToken(String token) {
        return validate(token, accessKey);
    }

    @Override
    public TokenValidationResult validateRefreshToken(String token) {
        return validate(token, refreshKey);
    }

    private TokenValidationResult validate(String token, SecretKey key) {
        try {
            var claims = Jwts.parser()
                    .verifyWith(key)
                    .build()
                    .parseSignedClaims(token)
                    .getPayload();

            return new TokenValidationResult(true, claims.getSubject());
        } catch (Exception e) {
            return new TokenValidationResult(false, null);
        }
    }
}
