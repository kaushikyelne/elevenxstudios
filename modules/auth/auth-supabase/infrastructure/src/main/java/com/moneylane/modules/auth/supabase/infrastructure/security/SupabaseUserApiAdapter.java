package com.moneylane.modules.auth.supabase.infrastructure.security;

import com.moneylane.modules.auth.common.application.port.out.ExternalIdentityProviderPort;
import com.moneylane.modules.auth.common.application.port.out.ExternalUserContext;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.Map;
import java.util.Optional;

@Component
public class SupabaseUserApiAdapter implements ExternalIdentityProviderPort {

    private final WebClient webClient;
    private final String serviceRoleKey;

    public SupabaseUserApiAdapter(
            WebClient.Builder webClientBuilder,
            @Value("${supabase.jwt.issuer}") String issuer,
            @Value("${supabase.jwt.serviceRoleKey}") String serviceRoleKey) {
        this.webClient = webClientBuilder.baseUrl(issuer).build();
        this.serviceRoleKey = serviceRoleKey;
    }

    @Override
    public Optional<ExternalUserContext> getDetailedUser(String externalId) {
        try {
            return webClient.get()
                    .uri("/admin/users/{id}", externalId)
                    .header("Authorization", "Bearer " + serviceRoleKey)
                    .retrieve()
                    .bodyToMono(SupabaseUserResponse.class)
                    .map(response -> new ExternalUserContext(
                            response.id(),
                            response.email(),
                            response.user_metadata() != null ? response.user_metadata() : Map.of()))
                    .blockOptional();
        } catch (Exception e) {
            // In a real app, log the error and handle specific HTTP status codes
            return Optional.empty();
        }
    }

    private record SupabaseUserResponse(
            String id,
            String email,
            Map<String, Object> user_metadata) {
    }
}
