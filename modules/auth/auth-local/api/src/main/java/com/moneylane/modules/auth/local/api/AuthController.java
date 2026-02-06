package com.moneylane.modules.auth.local.api;

import com.moneylane.modules.auth.local.application.port.in.AuthenticateUserUseCase;
import com.moneylane.modules.auth.local.application.port.in.RegisterUserUseCase;
import com.moneylane.modules.auth.common.domain.User;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.UUID;

@RestController
@RequestMapping("/api/v1/auth/local")
@RequiredArgsConstructor
public class AuthController {

        private final RegisterUserUseCase registerUserUseCase;
        private final AuthenticateUserUseCase authenticateUserUseCase;

        @PostMapping("/register")
        public ResponseEntity<RegistrationResponse> register(@RequestBody RegistrationRequest request) {
                User user = registerUserUseCase.register(new RegisterUserUseCase.Command(
                                request.email(),
                                request.password()));

                return ResponseEntity.ok(new RegistrationResponse(
                                user.getId().getValue(),
                                user.getEmail()));
        }

        @PostMapping("/login")
        public ResponseEntity<AuthResponse> login(@RequestBody LoginRequest request) {
                AuthenticateUserUseCase.AuthenticationResult result = authenticateUserUseCase.authenticate(
                                new AuthenticateUserUseCase.LoginCommand(request.email(), request.password()));

                return ResponseEntity.ok(new AuthResponse(
                                result.accessToken(),
                                result.refreshToken(),
                                result.expiresAt()));
        }

        @PostMapping("/refresh")
        public ResponseEntity<AuthResponse> refresh(@RequestBody RefreshRequest request) {
                AuthenticateUserUseCase.AuthenticationResult result = authenticateUserUseCase
                                .refreshToken(request.refreshToken());

                return ResponseEntity.ok(new AuthResponse(
                                result.accessToken(),
                                result.refreshToken(),
                                result.expiresAt()));
        }

        public record RegistrationRequest(String email, String password) {
        }

        public record RegistrationResponse(UUID id, String email) {
        }

        public record LoginRequest(String email, String password) {
        }

        public record RefreshRequest(String refreshToken) {
        }

        public record AuthResponse(String access_token, String refresh_token, long expires_at) {
        }
}
