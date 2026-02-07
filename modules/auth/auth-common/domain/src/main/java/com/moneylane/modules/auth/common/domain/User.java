package com.moneylane.modules.auth.common.domain;

import lombok.*;

@Getter
@Builder
@AllArgsConstructor
public class User {
    private final UserId id;
    private final String email;
    private final String passwordHash;
    private final String status;
    private final String externalProvider;
    private final String externalUserId;
}
