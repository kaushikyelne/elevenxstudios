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
}
