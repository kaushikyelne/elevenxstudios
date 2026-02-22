plugins {
    java
}

sourceSets {
    main {
        java {
            srcDirs("domain/src/main/java", "application/src/main/java", "infrastructure/src/main/java", "api/src/main/java")
        }
        resources {
            srcDirs("domain/src/main/resources", "application/src/main/resources", "infrastructure/src/main/resources", "api/src/main/resources")
        }
    }
    test {
        java {
            srcDirs("domain/src/test/java", "application/src/test/java", "infrastructure/src/test/java", "api/src/test/java")
        }
        resources {
            srcDirs("domain/src/test/resources", "application/src/test/resources", "infrastructure/src/test/resources", "api/src/test/resources")
        }
    }
}

dependencies {
    implementation(project(":modules:auth:auth-common"))
    implementation("org.springframework.boot:spring-boot-starter-security")
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("org.flywaydb:flyway-core")
    implementation("org.flywaydb:flyway-database-postgresql")
    runtimeOnly("org.postgresql:postgresql")

    implementation(project(":shared:kernel"))
    implementation(project(":shared:contracts"))
    implementation(project(":common:exception"))
    implementation(project(":common:util"))
    implementation("org.springframework.security:spring-security-crypto")
    implementation("io.jsonwebtoken:jjwt-api:0.12.6")
    runtimeOnly("io.jsonwebtoken:jjwt-impl:0.12.6")
    runtimeOnly("io.jsonwebtoken:jjwt-jackson:0.12.6")
}
