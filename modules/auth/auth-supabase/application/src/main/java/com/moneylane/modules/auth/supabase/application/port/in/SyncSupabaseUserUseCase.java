package com.moneylane.modules.auth.supabase.application.port.in;

import com.moneylane.modules.auth.common.domain.User;

public interface SyncSupabaseUserUseCase {
    User syncUser(String externalId, String email);
}
