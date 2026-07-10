# syntax=docker/dockerfile:1.4
FROM maven:3.9.6-eclipse-temurin-21-alpine AS build
WORKDIR /app

# Copy only the POM first so the dependency layer is cached
# and only re-runs when pom.xml changes.
COPY pom.xml .
RUN --mount=type=cache,target=/root/.m2 mvn dependency:go-offline -B

# Now copy sources and build. The .m2 cache mount means already
# downloaded dependencies are reused across builds.
COPY src ./src
RUN --mount=type=cache,target=/root/.m2 mvn clean package -DskipTests -B

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app

RUN addgroup -S spring && adduser -S spring -G spring
USER spring:spring

COPY --from=build /app/target/*.jar app.jar

ENV JAVA_OPTS="-Xms128m -Xmx300m -XX:+UseSerialGC -XX:+TieredCompilation -XX:TieredStopAtLevel=1 -XX:+UseCompressedOops -Xss256k -XX:MaxMetaspaceSize=128m -Djava.security.egd=file:/dev/./urandom -Dspring.jmx.enabled=false"

EXPOSE 8080

ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -Dserver.port=${PORT:-8080} -jar app.jar"]
