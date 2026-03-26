package com.moneylane.modules.auth.local.application.port.in;

import com.moneylane.modules.auth.common.domain.User;

public interface RegisterUserUseCase {
    User register(Command command);

    record Command(String email, String password) {
    }
}
