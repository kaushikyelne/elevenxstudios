sourceSets {
    main {
        java {
            srcDirs("application/src/main/java", "infrastructure/src/main/java", "api/src/main/java")
        }
        resources {
            srcDirs("application/src/main/resources", "infrastructure/src/main/resources", "api/src/main/resources")
        }
    }
}

dependencies {
    implementation(project(":modules:auth:auth-common"))
    implementation("org.springframework.boot:spring-boot-starter-security")
    implementation("org.springframework.boot:spring-boot-starter-oauth2-resource-server")
    implementation("org.springframework.boot:spring-boot-starter-web")
    compileOnly("org.projectlombok:lombok")
    annotationProcessor("org.projectlombok:lombok")
}
