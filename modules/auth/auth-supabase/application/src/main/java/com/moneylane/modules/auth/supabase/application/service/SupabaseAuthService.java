package com.moneylane.modules.auth.supabase.application.service;

import com.moneylane.modules.auth.common.application.port.out.ExternalAuthenticationResult;
import com.moneylane.modules.auth.common.application.port.out.ExternalIdentityProviderPort;
import com.moneylane.modules.auth.common.application.port.out.ExternalUserContext;
import com.moneylane.modules.auth.common.application.port.out.UserRepository;
import com.moneylane.modules.auth.common.domain.User;
import com.moneylane.modules.auth.common.domain.UserId;
import com.moneylane.modules.auth.supabase.application.port.in.LoginSupabaseUserUseCase;
import com.moneylane.modules.auth.supabase.application.port.in.SyncSupabaseUserUseCase;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class SupabaseAuthService implements SyncSupabaseUserUseCase, LoginSupabaseUserUseCase {

    private final UserRepository userRepository;
    private final ExternalIdentityProviderPort externalIdentityProvider;

    @Override
    public Optional<ExternalAuthenticationResult> login(String email, String password) {
        return externalIdentityProvider.authenticate(email, password)
                .map(authResult -> {
                    if (authResult.userContext() != null) {
                        syncUser(authResult.userContext().externalUserId(), authResult.userContext().email());
                    }
                    return authResult;
                });
    }

    @Override
    @Transactional
    public User syncUser(String externalUserId, String email) {

        return userRepository.findByExternalUserId(externalUserId)
                .orElseGet(() -> onboardNewUser(externalUserId, email));
    }

    private User onboardNewUser(String externalUserId, String email) {

        ExternalUserContext externalUser = externalIdentityProvider.getDetailedUser(externalUserId)
                .orElse(new ExternalUserContext(externalUserId, email, java.util.Map.of()));

        User user = User.builder()
                .id(new UserId(UUID.randomUUID()))
                .externalProvider("SUPABASE")
                .externalUserId(externalUser.externalUserId())
                .email(externalUser.email())
                .status("ACTIVE")
                .build();

        userRepository.save(user);
        return user;
    }
}
