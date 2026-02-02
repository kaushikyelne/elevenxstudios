package com.moneylane.modules.auth.infrastructure.persistence;

import com.moneylane.modules.auth.application.port.out.UserRepository;
import com.moneylane.modules.auth.domain.User;
import com.moneylane.modules.auth.domain.UserId;
import com.moneylane.modules.auth.domain.Role;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.Optional;

@Component
@RequiredArgsConstructor
public class JpaUserRepository implements UserRepository {

    private final SpringDataUserRepository repository;

    @Override
    public void save(User user) {
        UserEntity entity = mapToEntity(user);
        repository.save(entity);
    }

    @Override
    public Optional<User> findByEmail(String email) {
        return repository.findByEmail(email)
                .map(this::mapToDomain);
    }

    private UserEntity mapToEntity(User user) {
        return UserEntity.builder()
                .id(user.getId() != null ? user.getId().getValue() : null)
                .email(user.getEmail())
                .passwordHash(user.getPasswordHash())
                .role(user.getRole() != null ? user.getRole().name() : null)
                .status(user.getStatus())
                .build();
    }

    private User mapToDomain(UserEntity entity) {
        return User.builder()
                .id(new UserId(entity.getId()))
                .email(entity.getEmail())
                .passwordHash(entity.getPasswordHash())
                .role(entity.getRole() != null ? Role.valueOf(entity.getRole()) : null)
                .status(entity.getStatus())
                .build();
    }
}
