---
name: review-tests
description: "Use when the user asks to review, scan, or audit existing unit tests. Analyzes the test code against 'The Art of Unit Testing' and Google's Testing on the Toilet best practices. Identifies anti-patterns (logic in tests, over-mocking, poor naming) and provides a refactoring report."
allowed-tools: Read, Write, Glob, Grep, Bash, AskUserQuestion
---

# Review Tests Skill

You will act as an expert QA engineer and code reviewer, analyzing existing unit test files to ensure they comply with established unit testing best practices.

**Target to review:** $ARGUMENTS

## Quality Standards

- Focus on structural best practices and anti-patterns, not just syntax.
- Ground the review in established practice: prefer DAMP (descriptive, readable tests) over DRY when they conflict; test behaviors, not implementation details; keep cause and effect visible inside the test.
- Be incredibly strict about "Logic in Tests" (`if`, `for`) and Mocking boundaries.
- Provide actionable refactoring suggestions.

---

## Instructions

### Step 1: Code Context Analysis

1. **Read the target test file** specified in the arguments.
2. **Find and read the associated production code**. (For example, if testing `UserServiceTests.cs`, find `UserService.cs`). You must understand what the test is supposed to be testing.
3. **Read existing rules if available**: if the `generate-tests` skill is installed alongside this one, read its `rules/` directory for the specific language to ground your review in the same standards. If it is not installed, rely on the anti-pattern checklist in Step 2 — do not fail the review because the rules directory is absent.

### Step 2: Rule Enforcement (Scanning)

Analyze every test method in the target file for the following Anti-Patterns:

1. **Naming Convention:**
   - Are tests named using the format `Method_State_ExpectedBehavior`? 
   - *Example violation:* `testCalculateTotal()` instead of `CalculateTotal_ValidInput_ReturnsSum()`.
2. **Logic in Tests:**
   - Are there any `if/else`, `for`, `foreach`, `while`, or `try/catch` blocks inside the test? Tests should be straight-line code (KISS > DRY).
3. **Cause & Effect (Hidden Setup):**
   - Are critical test inputs being set up in `[SetUp]` / `@BeforeEach` instead of the test itself? A test reader shouldn't have to scroll up to understand the input state.
4. **Mocking Strategy (Over-mocking):**
   - Are Data Objects or DTOs being mocked instead of simply being instantiated (e.g., using Builders/Object Mothers)?
   - Are third-party library types being mocked directly instead of wrapping them in an owned interface?
5. **State vs. Interaction:**
   - Is the test over-relying on interaction verification (`.Received()`, `verify()`) when a simple state check or return value assertion would suffice?
6. **Single Responsibility (Too many asserts):**
   - Does the test assert multiple unrelated behaviors?

### Step 3: Output Generation

Generate a structured Markdown report that grades the test file. Use the following format:

```markdown
## Review Report: {TestFileName}

**Overall Grade:** [Pass / Needs Refactoring]

### 🔴 Violations Found

#### 1. {AntiPattern Name} (Lines X-Y)
- **Issue:** Explain why this violates best practices.
- **Snippet:** Show the offending code.
- **Fix:** Show the refactored, correct code.

### 🟢 Commendations
- Note anything the test did particularly well according to best practices.
```

### Step 4: Ask for User Review

After outputting the report, use the **AskUserQuestion tool** to ask the user if they want you to automatically apply the fixes:

```
Question: "Review complete. Would you like me to automatically apply these refactoring suggestions to the file?"
Header: "Next step"
Options:
  - Label: "Yes, apply fixes"
  - Label: "No, leave it as is"
```

### Step 5: Apply Fixes (If Approved)

If the user selects "Yes":

1. Keep the original file content available for reverting (e.g., note it or rely on `git diff`).
2. Use the `Write` tool to safely modify the test file and apply your refactoring suggestions.
3. Refactoring must preserve behavior coverage: never delete a test method or weaken an assertion as part of a "fix" without explicitly telling the user.

### Step 6: Verify the Refactored Tests

A refactor that breaks a passing suite is worse than no refactor. After applying fixes:

1. **Compile** the test project (max 3 fix attempts on errors).
2. **Run the modified test file/class only** (e.g. `dotnet test --filter "FullyQualifiedName~{TestClassName}"`, `npx vitest run {testFile}`, `npx jest {testFile}`) and verify every test still passes (max 3 fix attempts).
3. Do NOT modify production code to make tests pass.
4. If compilation or any test still fails after the attempt limits, **revert the file to its pre-refactor content** and report the failed refactoring to the user instead of delivering a broken suite.
