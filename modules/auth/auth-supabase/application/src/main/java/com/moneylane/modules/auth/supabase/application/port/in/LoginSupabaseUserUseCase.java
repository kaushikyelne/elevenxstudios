package com.moneylane.modules.auth.supabase.application.port.in;

import com.moneylane.modules.auth.common.application.port.out.ExternalAuthenticationResult;
import java.util.Optional;

public interface LoginSupabaseUserUseCase {
    Optional<ExternalAuthenticationResult> login(String email, String password);
}
