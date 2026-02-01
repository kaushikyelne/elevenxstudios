plugins {
    id("org.springframework.boot")
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation(project(":modules:transaction"))
    implementation(project(":modules:budget"))
    implementation(project(":modules:insight"))
    implementation(project(":shared:kernel"))
    implementation(project(":shared:contracts"))
    implementation(project(":common:exception"))
    implementation(project(":common:util"))
}
