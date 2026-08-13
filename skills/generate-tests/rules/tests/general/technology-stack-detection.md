---
title: Technology Stack Detection
impact: MEDIUM
impactDescription: ensures tests use correct frameworks and conventions for the project
tags: tests, technology, detection, frameworks, conventions
---

## Technology Stack Detection

When writing tests, first detect the programming language and technology stack from the project.

### Build/Package File Detection

| File | Language/Framework |
|------|-------------------|
| `*.csproj` / `*.sln` | C# (.NET) |
| `package.json` | JavaScript/TypeScript (npm/yarn) — then detect the test framework: `vitest.config.*` or `vitest` in devDependencies → Vitest; `jest.config.*` or a `"jest"` key in package.json → Jest. Never mix the two APIs. |
| `pyproject.toml` / `setup.py` / `requirements.txt` | Python |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `Gemfile` | Ruby |
| `mix.exs` | Elixir |
| `build.sbt` | Scala |
| `composer.json` | PHP |
| `Package.swift` | Swift |

### Test File Locations by Language

| Language | Test Location |
|----------|---------------|
| C# (.NET) | `<Project>.Tests/<ClassName>Tests.cs` |
| Python | `tests/test_<module_name>.py` or `<module>_test.py` |
| JavaScript/TypeScript | `__tests__/<name>.test.ts` or `<name>.test.js`; use `<name>.spec.ts` only when the project's existing tests already use `.spec.ts` (generate-tests treats `*.spec.ts` as a possible E2E signal) |
| Go | `<name>_test.go` (same directory as source) |
| Rust | `src/<name>.rs` with `#[cfg(test)]` module or `tests/` directory |
| Ruby | `spec/<name>_spec.rb` or `test/<name>_test.rb` |
| PHP | `tests/<ClassName>Test.php` |
| Elixir | `test/<name>_test.exs` |
| Scala | `src/test/scala/<package>/<ClassName>Spec.scala` |
| Swift | `Tests/<Name>Tests/<Name>Tests.swift` |

### Language-Specific Conventions

**Apply automatically based on detected stack:**

1. Use the idiomatic test framework for the detected language
2. Follow the language's naming conventions for test files and methods
3. Place test files in the standard location for that ecosystem
4. Use the language's preferred assertion style

**Incorrect:**

```csharp
// Using Python-style naming in C#
public void test_calculate_total() { ... }

// Placing C# tests in wrong location
// src/CalculatorTests.cs inside the production project (wrong)
```

**Correct:**

```csharp
// C# conventions
// Location: tests/Calculator.Tests/CalculatorTests.cs
public void CalculateTotal_ValidInput_ReturnsSum() { ... }
```

```python
# Python conventions
# Location: tests/test_calculator.py
def test_calculate_total_valid_input_returns_sum():
    ...
```
