sourceSets {
    main {
        java {
            srcDirs("domain/src/main/java", "application/src/main/java", "infrastructure/src/main/java", "api/src/main/java")
        }
        resources {
            srcDirs("domain/src/main/resources", "application/src/main/resources", "infrastructure/src/main/resources", "api/src/main/resources")
        }
    }
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-security")
    implementation("org.springframework.boot:spring-boot-starter-oauth2-resource-server")
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("org.springframework.boot:spring-boot-starter-validation")
    implementation("org.springdoc:springdoc-openapi-starter-webmvc-ui:2.5.0")
    implementation(project(":shared:kernel"))
    implementation(project(":shared:contracts"))
    implementation(project(":common:exception"))
    implementation(project(":common:util"))
}
