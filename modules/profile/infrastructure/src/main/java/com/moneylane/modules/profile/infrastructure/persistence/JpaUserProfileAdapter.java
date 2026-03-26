package com.moneylane.modules.profile.infrastructure.persistence;

import com.moneylane.modules.profile.application.port.out.UserProfilePort;
import com.moneylane.modules.profile.domain.UserProfile;
import com.moneylane.shared.kernel.UserId;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
@RequiredArgsConstructor
public class JpaUserProfileAdapter implements UserProfilePort {

    private final JpaUserProfileRepository repository;
    private final JpaUserProfileMapper mapper;

    @Override
    public Optional<UserProfile> findByUserId(UserId userId) {
        return repository.findById(userId.getValue())
                .map(mapper::toDomain);
    }

    @Override
    public UserProfile save(UserProfile profile) {
        JpaUserProfileEntity entity = mapper.toEntity(profile);
        JpaUserProfileEntity saved = repository.save(entity);
        return mapper.toDomain(saved);
    }
}
