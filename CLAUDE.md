# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A collection of AI agent skills (not a runnable application) for generating high-quality unit tests. Skills are installed into target projects via `npx openskills install` or `npx skills add`. The `skills/` directory contains only skill definitions and rule documents — no application code.

**Exception — `harness/` and `internal/`:** the top-level `harness/` directory contains small fixture projects (.NET, TypeScript) plus a scoring rubric used to evaluate skill output quality; `internal/` holds the repo-internal `eval-skills` and `improve-skill` skill definitions that drive it. Neither is installed into user projects — installers consume `skills/` only, which is exactly why the internal skills live outside it. See `specs/dotnet-typescript-unit-testing-skills.md`.

## Repository Structure

```
skills/
  generate-test-cases/    # Skill: analyze code → output test case list
    SKILL.md              # Skill definition (frontmatter + instructions)
    rules/general/        # General testing rules
  generate-tests/         # Skill: generate actual test code from cases
    SKILL.md
    rules/tests/
      general/            # General testing rules (superset of generate-test-cases rules)
      csharp/unit/        # C#-specific rules (xUnit, NSubstitute, AwesomeAssertions)
      typescript/unit/    # TypeScript/JavaScript rules (Vitest or Jest, detected)
      post-generation/    # Compilation + test-execution verification rules
  generate-tests-playwright/  # Skill: Playwright E2E/Component/API tests (POM) — draft
  review-tests/           # Skill: audit existing unit tests against best practices
internal/                 # Repo-internal skills — NOT installed into user projects
  eval-skills/            # Run harness, produce scorecard
  improve-skill/          # Eval → diagnose → propose rule edits
harness/                  # Eval-only fixtures + rubric + results (never installed)
  fixtures/dotnet/        # .NET fixture solution + golden test-case list
  fixtures/typescript/    # TS fixture package + golden test-case list
scripts/                  # Doc-generation pipeline + validate_skills.py (CI validator)
specs/                    # Design specs for repo changes
templates/
  AGENTS-SNIPPET.md       # Template users copy into their project's AGENTS.md
```

## Available Skills

| Command | Purpose |
|---------|---------|
| `/generate-tests <target>` | Generate unit tests for code. Handles the full workflow: analyzes code, outputs test cases for review, then generates test code. Supports C#/.NET (xUnit, NSubstitute, AwesomeAssertions) and TypeScript/JavaScript (Vitest or Jest). |
| `/generate-test-cases <target>` | Analyze code for test coverage and list needed test cases — without generating actual test code. Use for analysis-only. |
| `/generate-tests-playwright <target>` | Generate Playwright tests (E2E browser flows, Component, or API) for TS/JS targets, using the Page Object Model. |
| `/review-tests <target>` | Audit existing unit tests for anti-patterns (logic in tests, over-mocking, poor naming) and produce a refactoring report. |
| `/eval-skills [ecosystem]` | Repo-internal (`internal/eval-skills/`): run the harness fixtures through `generate-tests`, score against `harness/rubric.md`, write a scorecard. |
| `/improve-skill [ecosystem]` | Repo-internal (`internal/improve-skill/`): eval → classify failures → propose minimal rule edits as a reviewable branch/PR. Never auto-merges. |

## Workflow

`/generate-tests` is the primary skill — it handles the complete workflow internally:

1. Analyzes code and outputs a structured test case list
2. Asks the user to review test cases before proceeding
3. Generates test code
4. Verifies compilation

`/generate-test-cases` is available separately for analysis-only use cases (e.g., reviewing test coverage strategy without generating code).

## Rules

Each skill's `SKILL.md` lists which rule files it reads. When a skill is invoked, the skill definition instructs the agent to read the rule files from the skill's own `rules/` directory. The `generate-tests` skill has a superset of rules (includes language-specific and post-generation rules).

Key rule topics:
- **INCLUDE/EXCLUDE criteria** (`test-case-generation-strategy.md`) — what to test vs. skip
- **Naming** (`naming-conventions.md`) — `{method}_{state}_{outcome}` format
- **Structure** (`general-principles.md`) — Given-When-Then, `actual`/`expected` prefixes
- **Existing test awareness** (`existing-test-awareness.md`) — check for existing tests before generating; match project conventions; avoid duplicates
- **Code context analysis** (`code-context-analysis.md`) — read DTOs, entities, enums, and other dependency classes before writing tests
- **C# specifics** — xUnit + NSubstitute + AwesomeAssertions; Arrange-Act-Assert (AAA) structure comments; `WebApplicationFactory`/`TestServer`/Testcontainers FORBIDDEN in unit tests; capture DTOs with `Arg.Do`/`Arg.Is`, not `Arg.Any`; `FakeLogger` for log assertions; direct controller instantiation
- **TypeScript/JavaScript specifics** — Vitest or Jest (detected per project, APIs never mixed); DI-first mocking; snapshot tests FORBIDDEN for logic; always `await` async assertions; fake timers over real waits
- **Post-generation verification** — compilation verification (`compilation-verification.md`) AND test execution verification (`test-execution-verification.md`) — tests must both compile and pass

## Contributing

- Place general rules in `rules/general/` (or `rules/tests/general/` for generate-tests)
- Place language-specific rules in `rules/tests/{language}/unit/`
- **Keep general rules in sync**: General rules exist in TWO locations (`generate-test-cases/rules/general/` and `generate-tests/rules/tests/general/`). When adding or updating a general rule, copy the change to both directories
- When adding a new rule, also add it to the Rules Reference list in the relevant `SKILL.md` file(s)
- Run `python3 scripts/validate_skills.py --strict` before pushing — CI runs it on every PR and fails on broken rule references, orphan rules, frontmatter problems, or out-of-sync general rules
- Changes should land via PR with CODEOWNER review; run `/eval-skills` before merging rule changes
