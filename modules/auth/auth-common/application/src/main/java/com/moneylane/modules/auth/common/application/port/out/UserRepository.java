package com.moneylane.modules.auth.common.application.port.out;

import com.moneylane.modules.auth.common.domain.User;
import java.util.Optional;

public interface UserRepository {
    void save(User user);

    Optional<User> findByEmail(String email);
}
