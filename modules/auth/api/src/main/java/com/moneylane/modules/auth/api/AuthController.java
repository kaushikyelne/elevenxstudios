package com.moneylane.modules.auth.api;

import com.moneylane.modules.auth.application.port.in.RegisterUserUseCase;
import com.moneylane.modules.auth.domain.User;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.UUID;

@RestController
@RequestMapping("/api/v1/auth")
@RequiredArgsConstructor
public class AuthController {

    private final RegisterUserUseCase registerUserUseCase;

    @PostMapping("/register")
    public ResponseEntity<RegistrationResponse> register(@RequestBody RegistrationRequest request) {
        User user = registerUserUseCase.register(new RegisterUserUseCase.Command(
                request.email(),
                request.password()));

        return ResponseEntity.ok(new RegistrationResponse(
                user.getId().getValue(),
                user.getEmail(),
                user.getRole().name()));
    }

    public record RegistrationRequest(String email, String password) {
    }

    public record RegistrationResponse(UUID id, String email, String role) {
    }
}
