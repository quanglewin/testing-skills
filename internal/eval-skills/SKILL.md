---
name: eval-skills
description: "Repo-internal: evaluate the generate-tests skill against the harness fixtures and produce a scorecard. Use when asked to eval, score, or verify the test-generation skills, or before merging rule changes. Not for installation into user projects."
allowed-tools: Read, Write, Glob, Grep, Bash, Agent
---

# Evaluate Test-Generation Skills

You will run the `generate-tests` skill logic against one or more harness fixtures, score the
output against `harness/rubric.md`, and write a scorecard.

**Ecosystem(s) to evaluate:** $ARGUMENTS (default: all fixtures under `harness/fixtures/`)

## Prerequisites

- Read `harness/rubric.md` fully — it defines every dimension, gate, forbidden-pattern list, and the scorecard format.
- Confirm toolchains: `dotnet --version` for the .NET fixture, `node --version` for the TS fixture. If a toolchain is missing, skip that fixture and record SKIPPED in the scorecard — do not fake a result.
- Confirm the fixture is clean: `git status --porcelain harness/fixtures/` must be empty before starting.

## Process (per fixture)

### 1. Generate

Dispatch a subagent (general-purpose) whose prompt is: the full content of
`skills/generate-tests/SKILL.md` with `$ARGUMENTS` set to the fixture's primary target
(`harness/fixtures/dotnet/src/OrderFixture/OrderService.cs` or
`harness/fixtures/typescript/order-service/src/order-service.ts`), plus these overrides:

- Skip the Step 3 user-review gate — proceed as if the user approved (this is an automated eval).
- Write test files into the fixture's standard test location.
- The subagent must output its generated test-case list (Step 2 format) verbatim in its final report, so recall/precision can be scored against `expected-cases.md`.

Do NOT generate the tests yourself in this context — the point is to measure what the skill
produces from a cold start.

### 2. Hard gates

- .NET: `dotnet build harness/fixtures/dotnet/OrderService.sln` then `dotnet test` on the generated test project.
- TS: `npx tsc --noEmit` then `npx vitest run` inside the fixture (install deps with `npm install` first if `node_modules` is absent).
- Record exact exit codes and test counts. Nonzero exit = HARD gate failure; still complete the remaining dimensions for diagnostic value.

### 3. Recall / precision

- Read the fixture's `expected-cases.md` (golden list) and the subagent's generated case list.
- Match on covered code branch + expected outcome, not on exact names.
- Recall = matched golden / total golden. List every miss by golden-case name.
- Precision = count EXCLUDE-rule violations per the rubric. List each violation.

### 4. Forbidden patterns

Grep the generated test files using the rubric's per-ecosystem table. Ambiguous hits (e.g. a
legitimately irrelevant `Arg.Any`) get judged in step 5 with a note, not auto-failed.

### 5. Convention judgment

Read the generated test files and score the rubric's convention checklist honestly.
Quote the offending code for every failed item.

### 6. Scorecard + cleanup

- Write `harness/results/{YYYY-MM-DD}-{ecosystem}.md` in the rubric's scorecard format. If a file for today already exists, suffix `-2`, `-3`, ….
- Reset the fixture: delete generated test files and run `git checkout -- harness/fixtures/` so the working tree matches HEAD. Verify with `git status --porcelain harness/fixtures/` (must be empty).
- **Fixture diff check:** if the generation subagent modified anything under the fixture's `src/`, record it as an automatic convention failure ("modified production code") before resetting.

## Output

Print a summary table (one row per fixture: ecosystem, overall PASS/FAIL, failed dimensions)
and the path(s) of the scorecard file(s). Failing scorecards are the input to `/improve-skill`.

## Boundaries

- Never edit rule files, SKILL.md files, or fixture production code — this skill only measures.
- Never delete or rewrite existing scorecards in `harness/results/`.
- If the generation subagent errors out entirely, record the run as FAIL (generation error) with the error captured — do not retry more than once.
