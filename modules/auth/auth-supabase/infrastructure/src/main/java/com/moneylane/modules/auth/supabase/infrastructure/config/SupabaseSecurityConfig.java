package com.moneylane.modules.auth.supabase.infrastructure.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.annotation.Order;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
public class SupabaseSecurityConfig {

        @Bean
        @Order(1)
        public SecurityFilterChain supabaseSecurityFilterChain(HttpSecurity http) throws Exception {

                http
                                .securityMatcher("/api/v1/auth/**", "/api/v1/protected/**")
                                .csrf(csrf -> csrf.disable())
                                .sessionManagement(sm -> sm.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                                .authorizeHttpRequests(auth -> auth
                                                .requestMatchers("/api/v1/auth/login").permitAll()
                                                .anyRequest().authenticated())
                                .oauth2ResourceServer(oauth -> oauth.jwt());

                return http.build();
        }
}
