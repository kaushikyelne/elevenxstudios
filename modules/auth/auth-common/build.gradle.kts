plugins {
    java
}

sourceSets {
    main {
        java {
            srcDirs("domain/src/main/java", "application/src/main/java")
        }
        resources {
            srcDirs("domain/src/main/resources", "application/src/main/resources")
        }
    }
}

dependencies {
    implementation(project(":shared:kernel"))
    implementation(project(":shared:contracts"))
    compileOnly("org.projectlombok:lombok")
    annotationProcessor("org.projectlombok:lombok")
}
