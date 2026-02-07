package com.moneylane.modules.auth.common.application.port.out;

import java.util.Map;

public record ExternalUserContext(
                String externalUserId,
                String email,
                Map<String, Object> metadata) {
}
