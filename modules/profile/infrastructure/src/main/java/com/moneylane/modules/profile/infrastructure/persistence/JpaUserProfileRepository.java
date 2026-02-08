package com.moneylane.modules.profile.infrastructure.persistence;

import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;

public interface JpaUserProfileRepository extends JpaRepository<JpaUserProfileEntity, UUID> {
}
