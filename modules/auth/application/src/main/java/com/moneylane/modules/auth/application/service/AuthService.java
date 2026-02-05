package com.moneylane.modules.auth.application.service;

import com.moneylane.modules.auth.application.port.in.AuthenticateUserUseCase;
import com.moneylane.modules.auth.application.port.in.RegisterUserUseCase;
import com.moneylane.modules.auth.application.port.out.PasswordEncoderPort;
import com.moneylane.modules.auth.application.port.out.TokenServicePort;
import com.moneylane.modules.auth.application.port.out.UserRepository;

import com.moneylane.modules.auth.domain.User;
import com.moneylane.modules.auth.domain.UserId;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

@Service
@RequiredArgsConstructor
public class AuthService implements RegisterUserUseCase, AuthenticateUserUseCase {

    private final UserRepository userRepository;
    private final PasswordEncoderPort passwordEncoder;
    private final TokenServicePort tokenService;

    @Override
    @Transactional
    public User register(Command command) {
        validateEmail(command.email());
        validatePassword(command.password());

        if (userRepository.findByEmail(command.email()).isPresent()) {
            throw new RuntimeException("Email already exists");
        }

        String passwordHash = passwordEncoder.encode(command.password());

        User user = User.builder()
                .id(new UserId(UUID.randomUUID()))
                .email(command.email())
                .passwordHash(passwordHash)
                .status("ACTIVE")
                .build();

        userRepository.save(user);
        return user;
    }

    @Override
    @Transactional(readOnly = true)
    public AuthenticationResult authenticate(LoginCommand command) {
        User user = userRepository.findByEmail(command.email())
                .orElseThrow(() -> new RuntimeException("Invalid credentials"));

        if (!passwordEncoder.matches(command.password(), user.getPasswordHash())) {
            throw new RuntimeException("Invalid credentials");
        }

        TokenServicePort.TokenResult accessToken = tokenService.generateAccessToken(user.getEmail());

        TokenServicePort.TokenResult refreshToken = tokenService.generateRefreshToken(user.getEmail());

        return new AuthenticationResult(
                accessToken.token(),
                refreshToken.token(),
                accessToken.expiresAt().toEpochMilli());
    }

    @Override
    @Transactional(readOnly = true)
    public AuthenticationResult refreshToken(String refreshToken) {
        TokenServicePort.TokenValidationResult validation = tokenService.validateRefreshToken(refreshToken);

        if (!validation.isValid()) {
            throw new RuntimeException("Invalid refresh token");
        }

        User user = userRepository.findByEmail(validation.email())
                .orElseThrow(() -> new RuntimeException("User not found"));

        TokenServicePort.TokenResult newAccessToken = tokenService.generateAccessToken(user.getEmail());

        // Rotating the refresh token
        TokenServicePort.TokenResult newRefreshToken = tokenService.generateRefreshToken(user.getEmail());

        return new AuthenticationResult(
                newAccessToken.token(),
                newRefreshToken.token(),
                newAccessToken.expiresAt().toEpochMilli());
    }

    private void validateEmail(String email) {
        if (email == null || !email.matches("^[A-Za-z0-9+_.-]+@(.+)$")) {
            throw new RuntimeException("Invalid email format");
        }
    }

    private void validatePassword(String password) {
        if (password == null || password.length() < 8) {
            throw new RuntimeException("Password must be at least 8 characters long");
        }
    }
}
