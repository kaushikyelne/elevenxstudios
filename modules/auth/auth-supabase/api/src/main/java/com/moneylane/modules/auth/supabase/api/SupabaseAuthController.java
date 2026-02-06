package com.moneylane.modules.auth.supabase.api;

import com.moneylane.modules.auth.common.domain.User;
import com.moneylane.modules.auth.supabase.application.port.in.SyncSupabaseUserUseCase;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.UUID;

@RestController
@RequestMapping("/api/v1/auth/supabase")
@RequiredArgsConstructor
public class SupabaseAuthController {

    private final SyncSupabaseUserUseCase syncSupabaseUserUseCase;

    @GetMapping("/me")
    public ResponseEntity<UserResponse> getCurrentUser(@AuthenticationPrincipal Jwt jwt) {
        // Trigger sync and onboarding
        User user = syncSupabaseUserUseCase.syncUser(
                jwt.getSubject(),
                jwt.getClaim("email"));

        return ResponseEntity.ok(new UserResponse(
                user.getId().getValue(),
                user.getEmail(),
                jwt.getSubject(),
                user.getStatus()));
    }

    public record UserResponse(
            UUID id,
            String email,
            String providerUserId,
            String status) {
    }
}
