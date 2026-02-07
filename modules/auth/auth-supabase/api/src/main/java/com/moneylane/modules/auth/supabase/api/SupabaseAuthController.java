package com.moneylane.modules.auth.supabase.api;

import com.moneylane.modules.auth.common.domain.User;
import com.moneylane.modules.auth.supabase.application.port.in.LoginSupabaseUserUseCase;
import com.moneylane.modules.auth.supabase.application.port.in.SyncSupabaseUserUseCase;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/api/v1/auth")
@RequiredArgsConstructor
@io.swagger.v3.oas.annotations.tags.Tag(name = "Authentication", description = "Endpoints for Supabase and Local authentication")
public class SupabaseAuthController {

    private final SyncSupabaseUserUseCase syncUserUseCase;
    private final LoginSupabaseUserUseCase loginUseCase;

    @io.swagger.v3.oas.annotations.Operation(summary = "Login via Supabase", description = "Authenticates user with Supabase and returns a JWT")
    @PostMapping("/login")
    public ResponseEntity<LoginResponse> login(@RequestBody LoginRequest request) {
        return loginUseCase.login(request.email(), request.password())
                .map(result -> ResponseEntity.ok(new LoginResponse(
                        result.accessToken(),
                        result.refreshToken(),
                        result.expiresIn())))
                .orElse(ResponseEntity.status(HttpStatus.UNAUTHORIZED).build());
    }

    @io.swagger.v3.oas.annotations.Operation(summary = "Get current user profile", description = "Synchronizes and returns the current user's profile using the Bearer token")
    @GetMapping("/me")
    public ResponseEntity<UserResponse> me(@AuthenticationPrincipal Jwt jwt) {

        User user = syncUserUseCase.syncUser(
                jwt.getSubject(),
                jwt.getClaim("email"));

        return ResponseEntity.ok(new UserResponse(
                user.getId().getValue(),
                user.getEmail(),
                user.getExternalUserId(),
                user.getStatus()));
    }

    public record UserResponse(
            UUID id,
            String email,
            String providerUserId,
            String status) {
    }

    public record LoginRequest(String email, String password) {
    }

    public record LoginResponse(
            String accessToken,
            String refreshToken,
            long expiresIn) {
    }
}
