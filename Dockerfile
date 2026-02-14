# Build stage
FROM --platform=linux/amd64 gradle:8.10-jdk21 AS build
WORKDIR /home/gradle/src

# Copy project configuration for dependency caching
COPY --chown=gradle:gradle settings.gradle.kts build.gradle.kts ./

# Copy all build.gradle.kts files from modules to cache dependencies
# We use a trick to copy only the build files to keep the cache clean
COPY --chown=gradle:gradle modules/budget/build.gradle.kts modules/budget/
COPY --chown=gradle:gradle modules/insight/build.gradle.kts modules/insight/
COPY --chown=gradle:gradle modules/profile/build.gradle.kts modules/profile/
COPY --chown=gradle:gradle modules/transaction/build.gradle.kts modules/transaction/
COPY --chown=gradle:gradle modules/auth/auth-common/build.gradle.kts modules/auth/auth-common/
COPY --chown=gradle:gradle modules/auth/auth-local/build.gradle.kts modules/auth/auth-local/
COPY --chown=gradle:gradle modules/auth/auth-supabase/build.gradle.kts modules/auth/auth-supabase/
COPY --chown=gradle:gradle shared/kernel/build.gradle.kts shared/kernel/
COPY --chown=gradle:gradle shared/contracts/build.gradle.kts shared/contracts/
COPY --chown=gradle:gradle common/exception/build.gradle.kts common/exception/
COPY --chown=gradle:gradle common/util/build.gradle.kts common/util/
COPY --chown=gradle:gradle bootstrap/build.gradle.kts bootstrap/

# Dependency download
RUN gradle dependencies --no-daemon || true

# Copy full source and build
COPY --chown=gradle:gradle . .
RUN gradle :bootstrap:bootJar --no-daemon

# Run stage
# Alpine is used for smaller footprint and faster cold starts on Cloud Run
FROM --platform=linux/amd64 eclipse-temurin:21-jre-alpine
WORKDIR /app

# Security: Run as non-root user
RUN addgroup -S moneylane && adduser -S moneylane -G moneylane
USER moneylane

COPY --from=build /home/gradle/src/bootstrap/build/libs/*.jar app.jar

# Cloud Run dynamic PORT support (default to 8080)
ENV PORT 8080
EXPOSE 8080

# JVM Memory Optimizations for Containers:
# - MaxRAMPercentage: Allows the JVM to use a percentage of available container memory
# - server.port: Respects the Cloud Run dynamically assigned port
ENTRYPOINT ["sh", "-c", "java -XX:MaxRAMPercentage=75.0 -Dserver.port=${PORT} -jar app.jar"]
