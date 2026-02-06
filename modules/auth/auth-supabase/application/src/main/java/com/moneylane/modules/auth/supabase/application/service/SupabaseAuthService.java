package com.moneylane.modules.auth.supabase.application.service;

import com.moneylane.modules.auth.common.application.port.out.ExternalIdentityProviderPort;
import com.moneylane.modules.auth.common.application.port.out.ExternalUserContext;
import com.moneylane.modules.auth.common.application.port.out.UserRepository;
import com.moneylane.modules.auth.common.domain.User;
import com.moneylane.modules.auth.common.domain.UserId;
import com.moneylane.modules.auth.supabase.application.port.in.SyncSupabaseUserUseCase;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

@Service
@RequiredArgsConstructor
public class SupabaseAuthService implements SyncSupabaseUserUseCase {

    private final UserRepository userRepository;
    private final ExternalIdentityProviderPort externalIdentityProvider;

    @Override
    @Transactional
    public User syncUser(String externalId, String email) {
        // Idempotent check: Do we already have this user?
        // In a real scenario, you'd find by an 'external_id' column.
        // For this POC, we'll simplify and check by email.
        return userRepository.findByEmail(email)
                .orElseGet(() -> onboardNewUser(externalId, email));
    }

    private User onboardNewUser(String externalId, String email) {
        // Optionally fetch more details from the Admin API
        ExternalUserContext externalUser = externalIdentityProvider.getDetailedUser(externalId)
                .orElse(new ExternalUserContext(externalId, email, java.util.Map.of()));

        User newUser = User.builder()
                .id(new UserId(UUID.randomUUID()))
                .email(externalUser.email())
                .status("ACTIVE")
                .build();

        userRepository.save(newUser);
        return newUser;
    }
}
