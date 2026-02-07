package com.moneylane.modules.auth.supabase.infrastructure.security;

import com.moneylane.modules.auth.common.application.port.out.ExternalAuthenticationResult;
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
    private final String anonKey;

    public SupabaseUserApiAdapter(
            WebClient.Builder webClientBuilder,
            @Value("${supabase.auth.base-url}") String authBaseUrl,
            @Value("${supabase.admin.service-role-key}") String serviceRoleKey,
            @Value("${supabase.auth.anon-key}") String anonKey) {

        this.webClient = webClientBuilder.baseUrl(authBaseUrl).build();
        this.serviceRoleKey = serviceRoleKey;
        this.anonKey = anonKey;
    }

    @Override
    public Optional<ExternalUserContext> getDetailedUser(String externalUserId) {

        return webClient.get()
                .uri("/admin/users/{id}", externalUserId)
                .header("Authorization", "Bearer " + serviceRoleKey)
                .retrieve()
                .bodyToMono(SupabaseUserResponse.class)
                .map(resp -> new ExternalUserContext(
                        resp.id(),
                        resp.email(),
                        resp.user_metadata() != null ? resp.user_metadata() : Map.of()))
                .onErrorResume(ex -> Mono.empty())
                .blockOptional();
    }

    @Override
    public Optional<ExternalAuthenticationResult> authenticate(String email, String password) {
        return webClient.post()
                .uri("/token?grant_type=password")
                .header("apikey", anonKey)
                .bodyValue(Map.of("email", email, "password", password))
                .retrieve()
                .bodyToMono(SupabaseTokenResponse.class)
                .map(resp -> new ExternalAuthenticationResult(
                        resp.access_token(),
                        resp.refresh_token(),
                        resp.expires_in(),
                        resp.user() != null ? new ExternalUserContext(
                                resp.user().id(),
                                resp.user().email(),
                                resp.user().user_metadata() != null ? resp.user().user_metadata() : Map.of()) : null))
                .onErrorResume(ex -> Mono.empty())
                .blockOptional();
    }

    private record SupabaseUserResponse(
            String id,
            String email,
            Map<String, Object> user_metadata) {
    }

    private record SupabaseTokenResponse(
            String access_token,
            String refresh_token,
            long expires_in,
            SupabaseUserResponse user) {
    }
}
