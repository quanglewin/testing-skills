---
name: generate-test-cases
description: "Use when the user asks to analyze code for test coverage, list what test cases are needed, or review testing strategy — WITHOUT generating actual test code."
allowed-tools: Read, Glob, Grep, AskUserQuestion
---

# Generate Test Cases Skill

You will analyze code and generate a list of test cases that should be written for a given method/class. This skill outputs test case descriptions only — it does NOT generate actual test code.

**Target to analyze:** $ARGUMENTS

## Quality Standards

- Take your time to analyze the code thoroughly before listing test cases.
- Quality is more important than speed — read all relevant source files and rules carefully.
- Do not skip reading the dependency classes. Understanding the full context produces better test cases.

---

## Instructions

### Step 0: Resolve and Validate the Target

1. If the target above is empty, use the **AskUserQuestion tool** to ask what to analyze — do not guess.
2. Resolve the target to concrete file(s) with Glob/Grep. If a bare class/method name matches multiple files, list the matches and ask the user which one is intended. If the target is a directory or glob matching many files, confirm the scope with the user first. If it resolves outside the current project root, STOP and report it.
3. If the target cannot be found at all, follow Troubleshooting → "Target file not found".

### Step 1: Read Rules and Analyze Context

1. **Read the rules** from `./rules/general/` directory (see Rules Reference below)
2. **Read the target** source file/class/method specified above
3. **Read dependencies**: Follow imports to read DTOs, entities, enums, and other types referenced by the target (as specified in `code-context-analysis` rule)
4. **Check for existing tests**: Search for existing test classes covering this target (as specified in `existing-test-awareness` rule) — if found, read it fully and focus only on behaviors not yet covered
5. **Detect E2E context (TypeScript/JavaScript targets only)**: this skill analyzes UNIT test cases. If any of these signals is present, the user might actually want E2E tests instead:
   - `playwright.config.*` exists in the project, or `@playwright/test` is in devDependencies
   - The target file lives under an `e2e/`, `tests/e2e/`, or `playwright/` directory
   - The target is a page object, browser flow, or `*.spec.ts` following an E2E naming convention

   When a signal is present, use the **AskUserQuestion tool** BEFORE proceeding:
   ```
   Question: "This project uses Playwright. Analyze unit test cases for this target, or E2E tests?"
   Header: "Test type"
   Options:
     - Label: "Unit tests" / Description: "Continue with this skill"
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
3. Output the list of test cases in the specified format
4. Do NOT generate actual test code — only the test case descriptions

---

## Output Format

Use the target language's convention for the phase labels: **Arrange/Act/Assert** for C#/.NET (AAA — the .NET convention), **Given/When/Then** for TypeScript/JavaScript.

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

### Naming Convention
Test method name format: `{testedMethod}_{givenState}_{expectedOutcome}`

Examples:
- C#: `CalculateTotal_ValidProducts_ReturnsSum` (PascalCase segments)
- C#: `CalculateTotal_EmptyList_ThrowsArgumentException`
- TypeScript/JavaScript: `getUser_unauthorized_returns401` (camelCase segments)
- TypeScript/JavaScript: `getUser_forbidden_returns403`

---

## Troubleshooting

### Target file not found
If the specified target does not exist, inform the user with the exact path you searched and ask for clarification.

### Unsupported language
If the target code is in a language without specific rules, apply only the general rules and inform the user.

### All behaviors already covered
If the existing test class already covers all identified behaviors, output a summary stating that coverage is complete. List what is already tested. Do not invent additional test cases to justify the analysis.

---

## Example

```
User says: "/generate-test-cases src/Services/OrderService.cs"

Step 1: Agent reads rules, reads OrderService.cs, reads OrderRequest.cs,
        Order.cs (dependencies), checks for existing OrderServiceTests.cs.

Step 2: Agent outputs:

## Test Cases for OrderService.CreateOrder

### 1. CreateOrder_ValidRequest_SavesAndReturnsOrder
- **Arrange:** Valid OrderRequest with ProductId "product-1" and Quantity 5
- **Act:** CreateOrder is called
- **Assert:** Order is saved to repository and returned with generated ID
- **Code branch:** Success path

### 2. CreateOrder_EmptyProductId_ThrowsArgumentException
- **Arrange:** OrderRequest with empty ProductId
- **Act:** CreateOrder is called
- **Assert:** ArgumentException is thrown
- **Code branch:** Validation — ProductId empty check
...
```

---

## Rules Reference

**CRITICAL: You MUST read and apply all rules from the following files before generating test cases:**

> **Maintenance note:** General rules in `./rules/general/` are shared with the `generate-tests` skill (which has copies in `rules/tests/general/`). When updating rules, keep both locations in sync.

### General Rules (Always Apply)
- `./rules/general/test-case-generation-strategy.md` - INCLUDE/EXCLUDE criteria for test cases
- `./rules/general/naming-conventions.md` - Test naming format
- `./rules/general/general-principles.md` - Core testing principles
- `./rules/general/what-makes-good-test.md` - Clarity, Completeness, Conciseness, Resilience
- `./rules/general/keep-tests-focused.md` - One scenario per test
- `./rules/general/test-behaviors-not-methods.md` - Separate tests for behaviors
- `./rules/general/prefer-public-apis.md` - Test public APIs over private methods
- `./rules/general/cleanly-create-test-data.md` - Use helpers and builders for test data
- `./rules/general/keep-cause-effect-clear.md` - Effects follow causes immediately
- `./rules/general/no-logic-in-tests.md` - KISS > DRY, avoid logic in assertions
- `./rules/general/technology-stack-detection.md` - Detect language and framework
- `./rules/general/verify-relevant-arguments-only.md` - Only verify relevant mock arguments
- `./rules/general/existing-test-awareness.md` - Check for existing tests, avoid duplicates
- `./rules/general/code-context-analysis.md` - Read dependencies before analyzing
- `./rules/general/test-data-security.md` - No real secrets, PII, or production references in test data
