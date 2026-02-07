plugins {
    id("org.springframework.boot")
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
    implementation(project(":shared:kernel"))
    implementation(project(":shared:contracts"))
    implementation(project(":common:exception"))
    implementation(project(":common:util"))
}
