# Contributing Guidelines

Strict adherence to these guidelines is mandatory for all contributors to maintain repository integrity and clear operational history.

## 1. Branching Strategy

We operate under a strict, isolated branching methodology:

*   **`main`**: Protected production branch. **Direct commits are strictly forbidden.**
*   **`develop`**: The primary integration branch. All features and fixes must merge here before reaching production.
*   **`feature/*`**, **`fix/*`**, **`chore/*`**: Ephemeral working branches. These must branch off `develop` and merge back via Pull Request.

## 2. Commit Conventions

Every commit message must strictly adhere to the [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) specification.

**Structure:**
`<type>[optional scope]: <description>`

**Permitted Types:**
*   `feat:` A new feature or capability.
*   `fix:` A bug or error resolution.
*   `docs:` Documentation updates (e.g., README, CHANGELOG, CONTRIBUTING).
*   `style:` Formatting changes that do not affect logic (whitespace, linting).
*   `refactor:` Structural code changes that neither fix a bug nor add a feature.
*   `perf:` Optimization changes that improve performance.
*   `test:` Adding or modifying tests.
*   `chore:` Maintenance tasks, dependency updates, or build process adjustments.

*Example:* `feat(mlat): implement hex string decoder for ADS-B telemetry`

## 3. Versioning and Changelogs

*   **Semantic Versioning:** All repository releases adhere to [SemVer 2.0.0](https://semver.org/).
*   **Changelog:** Significant updates must be documented in `CHANGELOG.md` following the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) standard. No fragmented undocumented changes are permitted.
