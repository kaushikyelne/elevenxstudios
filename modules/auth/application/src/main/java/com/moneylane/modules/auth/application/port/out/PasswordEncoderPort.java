package com.moneylane.modules.auth.application.port.out;

public interface PasswordEncoderPort {
    String encode(CharSequence rawPassword);

    boolean matches(CharSequence rawPassword, String encodedPassword);
}
