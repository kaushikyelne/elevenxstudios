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
    test {
        java {
            srcDirs("domain/src/test/java", "application/src/test/java")
        }
        resources {
            srcDirs("domain/src/test/resources", "application/src/test/resources")
        }
    }
}

dependencies {
    implementation(project(":shared:kernel"))
    implementation(project(":shared:contracts"))
    compileOnly("org.projectlombok:lombok")
    annotationProcessor("org.projectlombok:lombok")
}
