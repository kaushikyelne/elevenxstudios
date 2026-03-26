package com.moneylane.modules.auth.supabase.api;

import com.moneylane.modules.auth.common.domain.User;
import com.moneylane.shared.kernel.UserId;
import com.moneylane.modules.auth.supabase.application.port.in.LoginSupabaseUserUseCase;
import com.moneylane.modules.auth.supabase.application.port.in.SyncSupabaseUserUseCase;

import io.swagger.v3.oas.annotations.tags.Tag;
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
@Tag(name = "Authentication")
public class SupabaseAuthController {

        private final SyncSupabaseUserUseCase syncUserUseCase;

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
}
