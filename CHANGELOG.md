# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **For consumers:** pin installs to a release tag for reproducible behavior,
> e.g. `npx openskills install quanglewin/testing-skills#v1.0.0`.

## [Unreleased]

- README install commands updated to the current repo (`quanglewin/testing-skills`); changelog restructured for the v1.0.0 release

## [1.0.0] - 2026-08-13

First tagged release ([v1.0.0](https://github.com/quanglewin/testing-skills/releases/tag/v1.0.0)). Four installable skills — `generate-tests`, `generate-test-cases`, `generate-tests-playwright`, `review-tests` — plus the internal eval harness. Enterprise-hardening changes included in this release:

### Added

- CI skill-structure validator: `scripts/validate_skills.py`, run on every PR and on pushes to `main` via GitHub Actions (`.github/workflows/validate-skills.yml`)
- New general rule `test-data-security.md` (no real secrets, PII, or production references in test data) — both rule locations
- Dependency-consent guardrail (never install/add packages without asking) and scoped-build guidance (build the test project, baseline pre-existing failures) in the post-generation rules
- Pre-existing-test protection (the fix/remove loop applies only to tests generated in the run), a removal circuit breaker, a post-run scope check (`git status`), and a Boundaries section in `generate-tests`
- Step 0 target resolution/validation (empty, ambiguous, directory/glob, or out-of-root targets) in `generate-tests` and `generate-test-cases`
- Post-fix compile-and-run verification with revert-on-failure in `review-tests`
- New rule content: HttpClient faking pattern (`domain-service-rules.md`), `InternalsVisibleTo` guidance (`prefer-public-apis.md`), `async void` test ban and Guid-determinism note (`csharp-test-template.md`), deterministic-values section (`assertion-rules.md`), mock clear/reset/restore semantics (`mocking-rules.md`), "neither framework present → ask" branch (`framework-detection.md`), Jest ≥30 `--testPathPatterns` note, `.spec.ts`-as-possible-E2E-signal naming guidance

### Changed

- Removed `context: fork` from the four user-facing skills' frontmatter so the mandatory AskUserQuestion review gates can reach the user
- `generate-test-cases` allowed-tools now includes `AskUserQuestion` (its E2E gate was blocked by the allowlist)
- `generate-tests-playwright` scope aligned to cover E2E browser flows, Component, and API tests (description, body dispatch, and all doc listings)
- Documentation consistency fixes: skill listings and rule-tree description in `AGENTS.md`, C# stack naming and structure diagram in `README.md`, skill entries in `templates/AGENTS-SNIPPET.md`
- Spec `specs/dotnet-typescript-unit-testing-skills.md` status: DRAFT → IMPLEMENTED
