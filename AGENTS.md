Follow [CONTRIBUTING.md](CONTRIBUTING.md) for code style, commit messages, pull requests and to learn the most useful build commands.

## Build Environment

- **Version**: `7.1.1-SNAPSHOT` (defined in `gradle.properties`).
- **JDK**: Toolchain JDK 25; API target `options.release = 17` (Java 17 compatibility).
- **Gradle**: 9.4.1 via `gradlew` (or `gradlew.bat` on Windows).
- **Kotlin**: 2.4.0 compiler, language/api level KOTLIN_2_3, JVM target 17.
- **Checkstyle**: `src/checkstyle/checkstyle.xml` (tabs-only indentation, Apache header via `checkstyle-header.txt`, no star imports, no System.out); tool version `13.2.0`.
- **Gradle JVM**: `-Xmx2g -XX:+HeapDumpOnOutOfMemoryError -XX:+EnableDynamicAgentLoading -XX:MaxMetaspaceSize=512m -Dfile.encoding=UTF-8`.
- **Gradle properties**: `--parallel`, `--build-cache`, `kotlin.stdlib.default.dependency=false`, `kotlin.jvm.target.validation.mode=IGNORE`.
- **Version catalog**: Centralized dependency versions in `gradle/libs.versions.toml`; BOMs managed via `dependencyManagement` in `build.gradle`.

Build a single module: `./gradlew :spring-integration-core:build`

## Code Conventions

- **Indentation**: tabs only — enforced by checkstyle (`RegexpSinglelineJava`).
- **Import order**: `java`, `javax`, `*`, `org.springframework` — separated groups, static imports sorted alphabetically.
- **Allowed static imports**: `org.assertj.core.api.Assertions.*`, `org.assertj.core.api.Assumptions.*`, `org.assertj.core.api.InstanceOfAssertFactories.*`, `org.mockito.BDDMockito.*`, `org.mockito.Mockito.*`, `org.mockito.AdditionalAnswers.*`, `org.mockito.ArgumentMatchers.*`, `org.mockito.AdditionalMatchers.*`, `org.springframework.integration.test.util.TestUtils.*`, `org.springframework.integration.test.mock.MockIntegration.*`, `org.awaitility.Awaitility.*`, `org.xmlunit.assertj3.XmlAssert.*`, `org.springframework.kafka.test.assertj.KafkaConditions.*`, `org.springframework.test.web.client.match.MockRestRequestMatchers.*`, `org.springframework.test.web.client.response.MockRestResponseCreators.*`, `org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*`, `org.springframework.test.web.servlet.result.MockMvcResultMatchers.*`, `org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.*`, `org.springframework.security.test.web.servlet.setup.SecurityMockMvcConfigurers.*`.
- **Javadoc**: `@author` with real name required on every class change; `@since` required for new public API. Build fails on Javadoc warnings (`Werror`, `doclint:syntax`).
- **Annotations**: compact style (`@Override`, not `@Override()`), `@MissingOverride` enforced.

## Testing Conventions

- **Framework**: JUnit 5 (Jupiter) + AssertJ + Mockito.
- **Additional test libs**: `reactor-test`, JUnit Pioneer (`@JUnitPioneer`), Testcontainers (`testcontainers-junit-jupiter`), Kotlin (`kotlin-reflect`, `kotlin-stdlib-jdk8`, `assertk`).
- **Long-running tests**: annotate with `@LongRunningTest` (from `org.springframework.integration.test.condition.LongRunningTest`, not `@LongRunningIntegrationTest`). These run only when `RUN_LONG_INTEGRATION_TESTS=true` is set (CI nightly). Invoke with `./gradlew clean testAll`.
- **Log control**: `@LogLevels` annotation to change Log4j levels per test method.
- **Test utility**: `TestUtils` in `spring-integration-test-support` (reflection helpers, `TestUtils.getPropertyValue(...)`). Integration testing framework in `spring-integration-test` (`mock/`, `context/`).
- **Test resources** include `src/test/java` (Java sources double as resources).
- **Test JVM**: `-Xshare:off`, `--enable-native-access=ALL-UNNAMED`, `enableAssertions=false`.
- **Environment**: `SI_FATAL_WHEN_NO_BEANFACTORY=true` set for all tests.
- **Console**: suppressed unless `gradle -i`.
- **Override test JDK**: `./gradlew test -PtestJavaVersion=17`.
- **Continue on failure**: add `--continue` to keep building other modules after failures.
- **Results**: per-module in `build/reports/tests/test/` (or `testAll/`).

Run a specific test class:
```
./gradlew :spring-integration-core:test --tests "org.springframework.integration.channel.DirectChannelTests"
```

## Module Conventions

Each protocol module (`spring-integration-<protocol>`) follows a consistent internal structure under `org.springframework.integration.<protocol>`. Common subdirectories include:

- `inbound/` and `outbound/` — channel adapter and gateway implementations
- `dsl/` — Java DSL `IntegrationFlow` specs (e.g. `Camel.java`, `ToCloudEventTransformerSpec.java`)
- `transformer/` — message transformation logic
- `config/` — XML namespace parsers and annotation processors (some use `config/xml/`)
- `support/` — utilities and management infrastructure
- `event/` — application event publishing (present in `websocket`, `ip`, `stream`, `stomp`, `mail`)
- `core/` — core abstractions (present in `jpa`, `mqtt`, `xmpp`, `event`)
- `session/` — remote session management (present in `sftp`, `smb`)
- `filters/` — file filtering strategies (present in `file`, `smb`)

Not all modules contain every subdirectory. Modules with simple functionality may have only a few (e.g. `syslog`: `inbound/`, `config/`; `graphql`: `outbound/`, `dsl/`). The `ip` module has deeper nesting with `tcp/` and `udp/` subpackages, each containing their own `inbound/` and `outbound/`.

**Dependencies**: All protocol modules get `spring-integration-core` as an `api` dependency. Optional dependencies use `optionalApi(...)` backed by `registerFeature('optional')` in the build. Dependency versions are managed centrally in `gradle/libs.versions.toml` via BOM platform declarations in `build.gradle`. The `spring-integration-test-support` module has **zero** Spring Integration runtime dependencies (avoids circular deps).
