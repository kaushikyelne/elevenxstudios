package com.moneylane.modules.auth.application.service;

import com.moneylane.modules.auth.application.port.in.RegisterUserUseCase;
import com.moneylane.modules.auth.application.port.out.PasswordEncoderPort;
import com.moneylane.modules.auth.application.port.out.UserRepository;
import com.moneylane.modules.auth.domain.Role;
import com.moneylane.modules.auth.domain.User;
import com.moneylane.modules.auth.domain.UserId;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

@Service
@RequiredArgsConstructor
public class AuthService implements RegisterUserUseCase {

    private final UserRepository userRepository;
    private final PasswordEncoderPort passwordEncoder;

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
                .role(Role.USER)
                .status("ACTIVE")
                .build();

        userRepository.save(user);
        return user;
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
