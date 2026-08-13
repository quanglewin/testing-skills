# AGENTS.md Snippet for Unit Test Skills

Add this snippet to your project's `AGENTS.md` file to enable AI agents to automatically discover and use the unit test generation skills.

## Quick Setup

If you don't have an `AGENTS.md` file yet, create one in your project root:

```bash
touch AGENTS.md
```

Then copy the content below into your `AGENTS.md`:

---

## Snippet to Copy

```markdown
# AGENTS.md

## Unit Test Generation

This project uses unit test generation skills.

### Available Skills

<available_skills>
  <skill>
    <name>generate-tests</name>
    <description>Use when the user asks to generate, create, or write unit tests for code. Analyzes the target code, produces a structured test case list for review, then generates test code. Supports C#/.NET (xUnit, NSubstitute, AwesomeAssertions) and TypeScript/JavaScript (Vitest or Jest).</description>
  </skill>
  <skill>
    <name>generate-test-cases</name>
    <description>Use when the user asks to analyze code for test coverage, list what test cases are needed, or review testing strategy — WITHOUT generating actual test code.</description>
  </skill>
  <skill>
    <name>generate-tests-playwright</name>
    <description>Use when the user asks to generate, create, or write Playwright tests (E2E browser flows, Component, or API) for TypeScript/JavaScript code. Analyzes the target flow, component, or API route, produces a structured test case list for review, then generates Playwright specs using the Page Object Model (POM).</description>
  </skill>
  <skill>
    <name>review-tests</name>
    <description>Use when the user asks to review, scan, or audit existing unit tests. Analyzes the test code against 'The Art of Unit Testing' and Google's Testing on the Toilet best practices. Identifies anti-patterns (logic in tests, over-mocking, poor naming) and provides a refactoring report.</description>
  </skill>
</available_skills>

### Key Principles

- INCLUDE: Each code branch, unique return value, each exception type
- EXCLUDE: Duplicate scenarios, collection size variations, speculative cases
- Format: `{method}_{state}_{outcome}` naming (`Method_State_Outcome` in C#)
- Structure: Arrange-Act-Assert (C#) / Given-When-Then (TS/JS) with `actual`/`expected` prefixes
- Languages: C# (xUnit + NSubstitute + AwesomeAssertions), TypeScript/JavaScript (Vitest or Jest — detected, never mixed)
```

---

## Why AGENTS.md?

According to [Vercel's research](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals):

| Configuration | Success Rate |
|---------------|--------------|
| Skills alone | 53% |
| Skills + instructions | 79% |
| **AGENTS.md** | **100%** |

AGENTS.md provides persistent context to agents on every turn, without requiring them to decide to load skills first.
