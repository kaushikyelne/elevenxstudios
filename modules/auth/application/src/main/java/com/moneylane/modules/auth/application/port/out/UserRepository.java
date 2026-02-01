package com.moneylane.modules.auth.application.port.out;

import com.moneylane.modules.auth.domain.User;
import java.util.Optional;

public interface UserRepository {
    void save(User user);

    Optional<User> findByEmail(String email);
}
