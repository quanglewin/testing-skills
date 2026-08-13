---
name: generate-tests-playwright
description: "Use when the user asks to generate, create, or write Playwright tests (E2E browser flows, Component, or API) for TypeScript/JavaScript code. Analyzes the target flow, component, or API route, produces a structured test case list for review, then generates Playwright specs using the Page Object Model (POM)."
allowed-tools: Read, Write, Glob, Grep, Bash, AskUserQuestion
---

# Generate Tests Skill (Playwright)

You will analyze TS/JS code (E2E browser flows, UI components, or API endpoints) and generate high-quality Playwright tests using the Page Object Model (POM). This is the designated hand-off target when `generate-tests` or `generate-test-cases` detects an E2E context.

**Target to test:** $ARGUMENTS

## Quality Standards

- Take your time to analyze the target flow, UI component, or API contract thoroughly before generating test cases.
- Use Playwright's web-first assertions (`expect(locator).toBeVisible()`).
- Always structure UI tests using the Page Object Model (POM).
- Never use `page.waitForTimeout()`. Rely on auto-waiting.

---

## Instructions

### Step 1: Read Rules and Analyze Context

1. **Read the relevant rules** from `./rules/playwright/` based on the target kind:
   - **E2E browser flow** (multi-page user journey) → `playwright/general/pom-rules.md` (Page Object Model structure)
   - **UI Component** → `playwright/component/playwright-component-rules.md` + `playwright/general/pom-rules.md`
   - **API route** → `playwright/api/playwright-api-rules.md`
2. **Read the target** source file.
3. **Check for existing tests**: Search for `{ComponentName}.spec.ts` in the test directory.

### Step 2: Generate Test Cases

1. Analyze ALL user flows, including success paths, error states, and edge cases.
2. Output the list of test cases in the format below — do NOT generate test code yet.

#### Test Case Output Format

```
## Test Cases for {ComponentName}

### 1. {testTitle}
- **Given:** {initial state/data}
- **When:** {user action}
- **Then:** {expected UI/API state}
```

### Step 3: Ask for User Review

Use the **AskUserQuestion tool** to ask the user:
```
Question: "Test cases are ready. Proceed with generating Playwright specs?"
Header: "Next step"
Options:
  - Label: "Yes, generate tests"
  - Label: "No, let me review first"
```

### Step 4: Generate Test Code

1. For UI tests, define a Page Object Model class first if one doesn't exist, or extend the existing one.
2. Generate the `.spec.ts` file.
3. Create or update the test file using the Write tool.

### Step 5: Verify Execution

1. Run `npx playwright test` on the generated test file.
2. Fix any failing tests — do NOT modify production code.

---

## Rules Reference

### Playwright Specific Rules
- `playwright/general/pom-rules.md` - Page Object Model enforcement (E2E browser flows and component page objects)
- `playwright/component/playwright-component-rules.md` - Rules for UI component testing
- `playwright/api/playwright-api-rules.md` - Rules for API testing
