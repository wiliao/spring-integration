Follow [CONTRIBUTING.md](CONTRIBUTING.md) for code style, commit messages, pull requests and to learn the most useful build commands.

## Build Environment

- **JDK**: Toolchain JDK 25; API target `options.release = 17` (Java 17 compatibility).
- **Gradle**: 9.4.1 via `gradlew` (or `gradlew.bat` on Windows).
- **Kotlin**: 2.4.0 compiler, language/api level KOTLIN_2_3, JVM target 17.
- **Checkstyle**: `src/checkstyle/checkstyle.xml` (tabs-only indentation, Apache header, no star imports, no System.out).
- **Gradle properties**: `--parallel`, `--build-cache`, `kotlin.stdlib.default.dependency=false`, `kotlin.jvm.target.validation.mode=IGNORE`.

Build a single module: `./gradlew :spring-integration-core:build`

## Code Conventions

- **Indentation**: tabs only — enforced by checkstyle (`RegexpSinglelineJava`).
- **Import order**: `java`, `javax`, `*`, `org.springframework` — separated groups, static imports sorted alphabetically.
- **Allowed static imports**: `org.assertj.core.api.Assertions.*`, `org.mockito.BDDMockito.*`, `org.mockito.Mockito.*`, `org.springframework.integration.test.util.TestUtils.*`, `org.awaitility.Awaitility.*`.
- **Javadoc**: `@author` with real name required on every class change; `@since` required for new public API. Build fails on Javadoc warnings (`Werror`, `doclint:syntax`).
- **Annotations**: compact style (`@Override`, not `@Override()`), `@MissingOverride` enforced.

## Testing Conventions

- **Framework**: JUnit 5 (Jupiter) + AssertJ + Mockito.
- **Long-running tests**: annotate with `@LongRunningTest` (not `@LongRunningIntegrationTest`). These run only when `RUN_LONG_INTEGRATION_TESTS=true` is set (CI nightly). Invoke with `./gradlew clean testAll`.
- **Log control**: `@LogLevels` annotation to change Log4j levels per test method.
- **Test utility**: `TestUtils` in `spring-integration-test-support` (reflection helpers, `TestUtils.getPropertyValue(...)`).
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

Each protocol module (`spring-integration-<protocol>`) follows a consistent internal structure under `org.springframework.integration.<protocol>`:

- `inbound/` and `outbound/` — channel adapter and gateway implementations
- `dsl/` — Java DSL `IntegrationFlow` specs (e.g. `CloudEvents.java`, `ToCloudEventTransformerSpec.java`)
- `transformer/` — message transformation logic
- `config/` — XML namespace parsers and annotation processors
- `support/` — utilities and management infrastructure

All protocol modules get `spring-integration-core` as an `api` dependency. The `spring-integration-test-support` module has **zero** Spring Integration runtime dependencies (avoids circular deps).
