package com.moneylane;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping;

@SpringBootApplication(scanBasePackages = { "com.moneylane" })
@ComponentScan(basePackages = {
        "com.moneylane",
        "com.moneylane.modules.auth.local.api",
        "com.moneylane.modules.auth.supabase.api",
        "com.moneylane.modules.auth.local.application",
        "com.moneylane.modules.auth.supabase.application",
        "com.moneylane.modules.auth.local.infrastructure",
        "com.moneylane.modules.auth.supabase.infrastructure"
})
@RestController
public class MoneyLaneApplication {

    @Autowired
    private RequestMappingHandlerMapping requestMappingHandlerMapping;

    public static void main(String[] args) {
        SpringApplication.run(MoneyLaneApplication.class, args);
    }

    @GetMapping("/api/v1/test")
    public String test() {
        return "ok";
    }

    @GetMapping("/api/v1/debug/mappings")
    public String debugMappings() {
        StringBuilder sb = new StringBuilder("Registered Mappings:\n");
        requestMappingHandlerMapping.getHandlerMethods().forEach((key, value) -> {
            sb.append(key).append(" -> ").append(value).append("\n");
        });
        return sb.toString();
    }
}
