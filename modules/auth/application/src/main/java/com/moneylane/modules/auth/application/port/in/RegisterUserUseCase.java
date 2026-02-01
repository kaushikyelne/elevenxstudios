package com.moneylane.modules.auth.application.port.in;

import com.moneylane.modules.auth.domain.User;

public interface RegisterUserUseCase {
    User register(Command command);

    record Command(String email, String password) {
    }
}
