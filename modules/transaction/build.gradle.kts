dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation(project(":shared:kernel"))
    implementation(project(":shared:contracts"))
    implementation(project(":common:exception"))
    implementation(project(":common:util"))
}
