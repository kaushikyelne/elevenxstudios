plugins {
    java
}

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
    implementation("org.springframework.boot:spring-boot-starter-webflux")
    implementation("org.springframework.boot:spring-boot-starter-oauth2-resource-server")
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("org.springdoc:springdoc-openapi-starter-webmvc-ui:2.5.0")
    implementation(project(":shared:kernel"))
    implementation(project(":shared:contracts"))
    compileOnly("org.projectlombok:lombok")
    annotationProcessor("org.projectlombok:lombok")
}
