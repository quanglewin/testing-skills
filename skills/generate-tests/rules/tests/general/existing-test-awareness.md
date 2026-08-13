---
title: Existing Test Awareness
impact: HIGH
impactDescription: prevents duplicate tests and ensures consistency with project conventions
tags: tests, awareness, duplicates, conventions, style
---

## Existing Test Awareness

Before generating tests, check what already exists. Match the project's testing conventions and avoid duplicating coverage.

### Before Generating: Check for Existing Tests

1. **Look for an existing test class** for the target:
   - Search for `{ClassName}Tests` in the test project
   - If found, read it fully before generating anything

2. **If an existing test class is found:**
   - Do NOT create a new test class — add missing test methods to the existing one
   - Preserve existing test structure, using directives, and helper methods
   - Follow the same patterns (naming, assertion style, setup approach) already used
   - Only add tests for behaviors not yet covered

3. **If no existing test class is found:**
   - Scan 2-3 neighboring test classes in the same namespace to learn project conventions
   - Match the style: using directive order, assertion library, naming pattern, comment style

### What to Match from Existing Tests

- **Assertion library**: Don't switch styles (e.g. AwesomeAssertions/FluentAssertions vs Shouldly vs plain xUnit `Assert`) — keep what the project already uses
- **Test data patterns**: If the project has a `TestDataFactory` or builders, use them
- **Base test classes**: If tests extend a `TestBase` or `IntegrationTestBase`, follow that pattern
- **Using directive style**: Match how the project imports assertion/substitute namespaces (e.g., `using static`, global usings)
- **Comment style**: If existing tests use `// given / when / then` vs `// arrange / act / assert`, match it

### What NOT to Do

**Incorrect:**

```csharp
// Creating a new test class when one already exists
// File: UserServiceTests.cs (NEW - duplicate!)
public class UserServiceTests
{
    // 10 test methods, 5 of which already exist in the old file
}
```

**Correct:**

```csharp
// Adding only missing tests to the existing file
// File: UserServiceTests.cs (EXISTING - appended to)
public class UserServiceTests
{
    // ... existing tests preserved as-is ...

    // New tests added below existing ones
    [Fact]
    public void UpdateUser_InvalidEmail_ThrowsValidationException()
    {
        // ...
    }
}
```

### Decision Checklist

Before writing any test code, verify:
- [ ] Searched for existing test class for the target
- [ ] Read existing tests to understand what's already covered
- [ ] Identified project test conventions from neighboring test files
- [ ] Confirmed which behaviors still need test coverage
