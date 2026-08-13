---
title: Test Naming Conventions
impact: HIGH
impactDescription: ensures consistent, readable test names that describe behavior
tags: tests, naming, conventions, readability
---

## Test Naming Conventions

Use consistent naming patterns that clearly describe the test scenario and expected outcome.

### Test Class Naming

Use the target language's idioms:
- `[TestedClass]Tests` (C#)
- `test_[module_name].py` (Python)
- `[name].test.ts` / `[name].test.js` (JavaScript/TypeScript); use `[name].spec.ts` only when the project's existing tests already use `.spec.ts` — note that generate-tests treats `*.spec.ts` as a possible E2E signal

### Test Method Naming

Format: `{testedMethod}_{givenState}_{expectedOutcome}`

In C# this renders in PascalCase (`Method_State_Outcome`); in TypeScript/JavaScript it stays camelCase.

**Incorrect:**

```csharp
// Too vague
[Fact]
public void TestCalculate() { ... }

// No outcome described
[Fact]
public void CalculateTotal_ValidProducts() { ... }

// Implementation details instead of behavior
[Fact]
public void CalculateTotal_UsesLinq_ReturnsSum() { ... }
```

**Correct:**

```csharp
// Clear state and outcome
[Fact]
public void CalculateTotal_ValidProducts_ReturnsSum() { ... }

[Fact]
public void CalculateTotal_EmptyList_ThrowsArgumentException() { ... }

[Fact]
public void GetUser_Unauthorized_Returns401() { ... }

[Fact]
public void GetUser_Forbidden_Returns403() { ... }

[Fact]
public void SaveOrder_ValidOrder_PersistsToDatabase() { ... }

[Fact]
public void DeleteUser_NonExistentId_ThrowsNotFoundException() { ... }
```

### Naming Guidelines

1. **Be specific about the state/condition** - "ValidProducts" not "GoodInput"
2. **Be specific about the outcome** - "Returns401" not "Fails"
3. **Use domain language** - "Unauthorized" not "NoToken"
4. **Avoid technical jargon** - describe behavior, not implementation
