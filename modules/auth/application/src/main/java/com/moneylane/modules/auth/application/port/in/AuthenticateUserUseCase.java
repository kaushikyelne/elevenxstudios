package com.moneylane.modules.auth.application.port.in;

public interface AuthenticateUserUseCase {
    AuthenticationResult authenticate(LoginCommand command);

    AuthenticationResult refreshToken(String refreshToken);

    record LoginCommand(String email, String password) {
    }

    record AuthenticationResult(String accessToken, String refreshToken, long expiresAt) {
    }
}
