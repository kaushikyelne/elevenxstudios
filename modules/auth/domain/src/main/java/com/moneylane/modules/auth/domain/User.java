package com.moneylane.modules.auth.domain;

import lombok.*;

@Getter
@Builder
@AllArgsConstructor
public class User {
    private final UserId id;
    private final String email;
    private final String passwordHash;
    private final Role role;
    private final String status;
}
