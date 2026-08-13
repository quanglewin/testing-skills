---
name: generate-tests
description: "Use when the user asks to generate, create, or write unit tests for code. Analyzes the target code, produces a structured test case list for review, then generates test code. Supports C#/.NET (xUnit, NSubstitute, AwesomeAssertions) and TypeScript/JavaScript (Vitest or Jest)."
allowed-tools: Read, Write, Glob, Grep, Bash, AskUserQuestion
---

# Generate Tests Skill

You will analyze code and generate high-quality unit tests for a given target.

**Target to test:** $ARGUMENTS

## Quality Standards

- Take your time to analyze the code thoroughly before generating test cases.
- Quality is more important than speed — read all relevant source files and rules carefully.
- Do not skip any step in the workflow below. Every step exists for a reason.
- Do not take shortcuts with test data — read the actual classes to use correct constructors and fields.

---

## Instructions

### Step 0: Resolve and Validate the Target

1. If the target above is empty, use the **AskUserQuestion tool** to ask what to test — do not guess.
2. Resolve the target to concrete file(s) with Glob/Grep:
   - Exactly one file → proceed.
   - A bare class/method name matching multiple files → list the matches and ask the user which one is intended.
   - A directory or glob matching many files → confirm the scope with the user before proceeding.
   - A path resolving outside the current project root → STOP and report it; never follow paths out of the workspace.
3. If the target cannot be found at all, follow Troubleshooting → "Target file not found".

### Step 1: Read Rules and Analyze Context

1. **Read the relevant rules** from `./rules/tests/` based on code type (see Rules Reference below)
2. **Read the target** source file/class/method
3. **Read dependencies**: Follow imports to read DTOs, entities, enums, custom exceptions, and other types referenced by the target (as specified in `code-context-analysis` rule)
4. **Check for existing tests**: Search for `{ClassName}Test` or `{ClassName}Tests` in the test directory (as specified in `existing-test-awareness` rule)
   - If found, read fully — you will add missing tests to it, not create a new file
   - If not found, scan 2-3 neighboring test classes to learn project conventions
5. **Detect E2E context (TypeScript/JavaScript targets only)**: this skill generates UNIT tests. If any of these signals is present, the user might actually want E2E tests instead:
   - `playwright.config.*` exists in the project, or `@playwright/test` is in devDependencies
   - The target file lives under an `e2e/`, `tests/e2e/`, or `playwright/` directory
   - The target is a page object, browser flow, or `*.spec.ts` following an E2E naming convention

   When a signal is present, use the **AskUserQuestion tool** BEFORE proceeding:
   ```
   Question: "This project uses Playwright. Generate unit tests for this target, or E2E tests?"
   Header: "Test type"
   Options:
     - Label: "Unit tests" / Description: "Continue with this skill (Vitest/Jest unit tests, mocked dependencies)"
     - Label: "E2E tests" / Description: "Stop — use the generate-tests-playwright skill instead"
   ```
   - "Unit tests" → continue with this workflow
   - "E2E tests" → STOP and tell the user to run `/generate-tests-playwright <target>` (separate skill)

   Do NOT auto-switch: a project can legitimately need unit tests for the same file Playwright covers end-to-end. C# targets skip this step.

### Step 2: Generate Test Cases

1. Analyze ALL code branches, including:
   - Success paths
   - Error/exception paths
   - Validation logic
   - Private/protected methods called by the target
   - Security annotations (if present)
2. Apply the INCLUDE/EXCLUDE rules strictly
3. Output the list of test cases in the format below — do NOT generate test code yet

#### Test Case Output Format

Use the target language's convention for the phase labels: **Arrange/Act/Assert** for C#/.NET (AAA — the .NET convention, per xUnit and Microsoft guidance), **Given/When/Then** for TypeScript/JavaScript.

C# targets:

```
## Test Cases for {ClassName}.{MethodName}

### 1. {TestMethodName}
- **Arrange:** {preconditions/input state}
- **Act:** {action being tested}
- **Assert:** {expected outcome}
- **Code branch:** {which code path this covers}

### 2. {TestMethodName}
...
```

TypeScript/JavaScript targets:

```
## Test Cases for {ClassName}.{methodName}

### 1. {testMethodName}
- **Given:** {preconditions/input state}
- **When:** {action being tested}
- **Then:** {expected outcome}
- **Code branch:** {which code path this covers}
```

#### Naming Convention
Test method name format: `{testedMethod}_{givenState}_{expectedOutcome}`

Examples:
- `calculateTotal_validProducts_returnsSum`
- `calculateTotal_emptyList_throwsRangeError`
- `getUser_unauthorized_returns401`

Language renderings of the same convention:
- C#: `CalculateTotal_ValidProducts_ReturnsSum` (PascalCase segments)
- TypeScript / JavaScript: `calculateTotal_validProducts_returnsSum` (camelCase segments)

### Step 3: Ask for User Review

After outputting test cases, use the **AskUserQuestion tool** to ask the user:
```
Question: "Test cases are ready. Proceed with generating test code?"
Header: "Next step"
Options:
  - Label: "Yes, generate tests" / Description: "Proceed to generate test files from the test cases above"
  - Label: "No, let me review first" / Description: "Stop here so I can review and adjust the test cases"
```

- If user selects "Yes", proceed to Step 4
- If user selects "No", STOP and wait for further instructions

### Step 4: Generate Test Code

1. Determine the language (per `technology-stack-detection.md`), then the code type, and apply the matching rules:

   **C# / .NET** (`rules/tests/csharp/unit/`):
   - **Controller** → `controller-test-rules.md` (direct instantiation + ActionResult assertions; WebApplicationFactory FORBIDDEN)
   - **Service / Domain logic** → `domain-service-rules.md` (NSubstitute patterns, constructor injection)
   - **All C# code** → Always apply `csharp-test-template.md`, `substitute-rules.md`, `json-serialization.md`
   - **Target logs via `ILogger`** → also apply `logging-rules.md` (FakeLogger; never verify on a substituted `ILogger` — extension-method trap)
   - **Structure comments**: use `// Arrange` / `// Act` / `// Assert` (AAA — the .NET convention), not `// Given/When/Then`

   **TypeScript / JavaScript** (`rules/tests/typescript/unit/` — applies to plain JS too):
   - **First** → `framework-detection.md` (Vitest vs Jest — never mix APIs)
   - **All TS/JS code** → Always apply `ts-test-template.md`, `mocking-rules.md`, `assertion-rules.md`; add `async-testing.md` when the target has async paths or timers

   **Any language, other code types** (Repository / Messaging / etc.) → apply that language's baseline rules — C#: `csharp/unit/domain-service-rules.md`; TypeScript/JavaScript: `typescript/unit/ts-test-template.md` + `mocking-rules.md` — and inform the user that type-specific rules are not yet available

   **Precedence:** when an existing test class or the project's conventions conflict with template defaults (structure comments, assertion library, naming), the existing project conventions win (per `existing-test-awareness.md`). Template defaults apply only when no existing tests are found.
2. If an existing test class was found in Step 1, add new test methods to it (do not create a duplicate file)
3. Generate tests following all rules and the test cases from Step 2
4. Create or update the test file using the Write tool

### Step 5: Verify Compilation and Execution

1. Run compilation **scoped to the test project** and fix any issues (max 5 attempts — see `compilation-verification.md`)
   - If a required test package is missing, do NOT install or add it silently — ask the user first (dependency guardrail in `compilation-verification.md`)
2. Run **only the generated test class/file** to verify all tests pass (see `test-execution-verification.md`) — never kick off the whole repo's build/test pipeline
3. Fix any failing tests — do NOT modify production code
   - The fix/remove loop applies ONLY to test methods generated in this run. NEVER delete, rewrite, or disable a pre-existing test method. If a pre-existing test fails — or starts failing after your additions — stop, revert your additions if they caused it, and report to the user.
4. If a generated test cannot be fixed after 3 attempts, remove it, leave the `// TODO:` record required by `test-execution-verification.md`, and inform the user
   - **Circuit breaker:** if more than 2 generated tests (or more than 25% of them) would be removed, STOP and ask the user how to proceed instead of removing more
5. **Verify scope before finishing:** run `git status --porcelain` (or `git diff --name-only`) and confirm the only changed/added files are the generated or updated test file(s) — plus a dependency config change only if the user explicitly approved one. Revert anything else and report it.
6. In the final summary, list every delivered test and every approved test case that was removed or skipped, so any coverage reduction is visible to the user.

---

## Boundaries

Hard limits — no step in this workflow overrides them:

- NEVER modify production code. Only test files (and, with explicit user approval, the test project's dependency config) may change.
- NEVER delete, rewrite, or disable a pre-existing test method or test file.
- NEVER add package dependencies or run installers (`npm install`, `dotnet add package`, editing `.csproj`/`package.json`) without asking the user first.
- NEVER run `git commit`, `git push`, or any other git state-changing command.
- NEVER create or modify files outside the test project/directory.
- Test data must follow `test-data-security.md`: no real secrets, credentials, PII, or production endpoints.

---

## Troubleshooting

### Target file not found
If the specified target does not exist, inform the user with the exact path you searched and ask for clarification.

### Unsupported language
If the target code is in a language without specific rules (not C#, TypeScript, or JavaScript), apply only the general rules and inform the user that language-specific conventions may need manual review.

### Compilation keeps failing
If compilation fails after 5 attempts:
1. Stop and show the user the remaining errors
2. Suggest possible causes (missing dependencies, incompatible versions)
3. Ask the user to resolve the build issue before continuing

### Tests fail due to production code behavior
If tests fail because the production code behaves differently than expected:
1. Do NOT modify production code
2. Fix the test to match actual behavior
3. If the behavior seems like a bug, add a comment: `// NOTE: current behavior may be a bug — {description}`

---

## Example

```
User says: "/generate-tests src/Services/OrderService.cs"

Step 1: Agent reads rules, reads OrderService.cs, reads OrderRequest.cs,
        Order.cs, IOrderRepository.cs (dependencies), checks for
        existing OrderServiceTests.cs

Step 2: Agent outputs 7 test cases covering:
        - CreateOrder success path
        - CreateOrder with invalid request (validation)
        - ProcessPayment success
        - ProcessPayment failure
        - CalculateTotal with products
        - CalculateTotal with empty list
        - CancelOrder for non-existent order

Step 3: Agent asks user to review. User says "Yes, generate tests".

Step 4: Agent generates OrderServiceTests.cs with NSubstitute substitutes for
        the repository and payment gateway, AAA structure, 7 test methods.

Step 5: Agent runs `dotnet test --filter "FullyQualifiedName~OrderServiceTests"`,
        all tests pass.

Result: Complete test file delivered with 7 passing tests.
```

---

## Rules Reference

**CRITICAL: You MUST read and apply all relevant rules from the `./rules/tests/` directory.**

> **Maintenance note:** General rules in `./rules/tests/general/` are shared with the `generate-test-cases` skill (which has copies in `rules/general/`). When updating rules, keep both locations in sync.

### General Rules (Always Apply)
- `general/test-case-generation-strategy.md` - INCLUDE/EXCLUDE criteria
- `general/naming-conventions.md` - Test naming format
- `general/general-principles.md` - Core testing principles (Given-When-Then, actual/expected)
- `general/technology-stack-detection.md` - Detect language and framework
- `general/what-makes-good-test.md` - Clarity, Completeness, Conciseness, Resilience
- `general/cleanly-create-test-data.md` - Use helpers and builders for test data
- `general/keep-cause-effect-clear.md` - Effects follow causes immediately
- `general/no-logic-in-tests.md` - KISS > DRY, avoid logic in assertions
- `general/keep-tests-focused.md` - One scenario per test
- `general/test-behaviors-not-methods.md` - Separate tests for behaviors
- `general/verify-relevant-arguments-only.md` - Only verify relevant mock arguments
- `general/prefer-public-apis.md` - Test public APIs over private methods
- `general/existing-test-awareness.md` - Check for existing tests, match project conventions
- `general/code-context-analysis.md` - Read dependencies before writing tests
- `general/test-data-security.md` - No real secrets, PII, or production references in test data

### C# Unit Tests
- `csharp/unit/csharp-test-template.md` - xUnit template, FORBIDDEN patterns (WebApplicationFactory, Testcontainers)
- `csharp/unit/substitute-rules.md` - NSubstitute: capture DTOs with Arg.Do/Arg.Is, not Arg.Any
- `csharp/unit/json-serialization.md` - Raw string literals, no JsonSerializer.Serialize in tests
- `csharp/unit/logging-rules.md` - FakeLogger for log verification (ILogger extension-method trap)
- `csharp/unit/domain-service-rules.md` - NSubstitute patterns for services, constructor injection
- `csharp/unit/controller-test-rules.md` - Direct controller instantiation, ActionResult assertions

### TypeScript/JavaScript Unit Tests
- `typescript/unit/ts-test-template.md` - describe/it structure, typed test data
- `typescript/unit/framework-detection.md` - Vitest vs Jest detection and API mapping
- `typescript/unit/mocking-rules.md` - DI-first mocking, vi.mock hoisting pitfalls
- `typescript/unit/assertion-rules.md` - toBe/toEqual/toStrictEqual, snapshot tests FORBIDDEN for logic
- `typescript/unit/async-testing.md` - await rejects/resolves, fake timers, no done() callbacks

### Post-Generation
- `post-generation/compilation-verification.md` - Verify compilation
- `post-generation/test-execution-verification.md` - Verify tests pass
