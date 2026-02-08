plugins {
    id("org.springframework.boot")
}

tasks.named<org.springframework.boot.gradle.tasks.run.BootRun>("bootRun") {
    // Load .env file if it exists
    val envFile = file("../.env")
    if (envFile.exists()) {
        envFile.readLines()
            .filter { it.isNotBlank() && !it.startsWith("#") && it.contains("=") }
            .forEach { line ->
                val parts = line.split("=", limit = 2)
                if (parts.size == 2) {
                    val key = parts[0].trim()
                    val value = parts[1].trim().removeSurrounding("\"").removeSurrounding("'")
                    environment(key, value)
                    println("Loaded env: $key")
                }
            }
    }
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-security")
    implementation("org.springdoc:springdoc-openapi-starter-webmvc-ui:2.5.0")
    implementation(project(":modules:auth:auth-local"))
    implementation(project(":modules:auth:auth-supabase"))
    implementation(project(":modules:auth:auth-common"))
    implementation(project(":modules:transaction"))
    implementation(project(":modules:budget"))
    implementation(project(":modules:insight"))
    implementation(project(":modules:profile"))
    implementation(project(":shared:kernel"))
    implementation(project(":shared:contracts"))
    implementation(project(":common:exception"))
    implementation(project(":common:util"))
}
