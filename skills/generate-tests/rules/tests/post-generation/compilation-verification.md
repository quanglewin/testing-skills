---
title: Post-Generation Compilation Verification
impact: HIGH
impactDescription: ensures generated tests compile successfully before delivery
tags: tests, compilation, verification, build, ci
---

## Post-Generation Compilation Verification

After generating test files, verify they compile successfully. Fix any issues before completing the task.

### Compilation Commands by Build System

**Scope the build to the test project.** In a large enterprise repo, building the whole solution or type-checking the whole monorepo (up to 5 times in the fix loop) is expensive and drags unrelated errors into scope.

| Build System | Command |
|--------------|---------|
| .NET | `dotnet build path/to/TestProject.csproj` (not the whole solution) |
| npm/yarn (TypeScript) | `npx tsc --noEmit -p <tsconfig covering the test file>` or the package's own `npm run build` |
| Python | `python -m py_compile <test_file>` |
| Go | `go build ./...` |
| Rust | `cargo check --tests` |
| Mix (Elixir) | `mix compile` |
| Swift | `swift build` |

### Process

1. **Baseline first**: if the test project already fails to build BEFORE your test file is added, STOP and report the pre-existing build failure — do not try to fix unrelated build errors
2. **Create the test file** in the correct location
3. **Run compilation** scoped to the test project
4. **If compilation fails:**
   - Read the error message
   - Fix the issue (missing using directives, wrong types, syntax errors)
   - If a required package is missing, follow the Dependency Guardrail below — never add it silently
   - Re-run compilation
5. **Repeat until successful** (max 5 attempts)

### Dependency Guardrail

Enterprise projects have curated package feeds, central version management, and dependency-approval processes. Therefore:

- **NEVER add a package reference or run an install command (`npm install`, `dotnet add package`, editing `.csproj`/`package.json`) without asking the user first.** Use AskUserQuestion, naming the exact package and why it is needed.
- Once approved, **prefer the version already used elsewhere in the solution/monorepo** over a hardcoded pin. In .NET, respect Central Package Management if present (`Directory.Packages.props` — no `Version` attribute on the `PackageReference` in that case); otherwise prefer `dotnet add package <Name>` so tooling resolves a compatible version. In npm workspaces, match the version other packages use.
- Only the **test project's** config may change. Never touch production project configs or lockfiles beyond what the approved test-dependency change requires.

### Common Issues and Fixes

**Missing Using Directives (C#):**
```csharp
// Error: The type or namespace name 'Fact' could not be found
// Fix: Add the missing using directives
using Xunit;
using NSubstitute;
using FluentAssertions;
```

**Missing Dependencies (.NET)** — only after user approval per the Dependency Guardrail:
```bash
# Preferred: let tooling resolve a compatible version (or match the version
# already used elsewhere in the solution / Directory.Packages.props)
dotnet add path/to/TestProject.csproj package NSubstitute
dotnet add path/to/TestProject.csproj package AwesomeAssertions
```

**Missing Dependencies (npm)** — only after user approval per the Dependency Guardrail:
```bash
# Add to devDependencies; match the version other workspace packages use
npm install --save-dev vitest
```

**Wrong Namespace (C#):**
```csharp
// Error: The type or namespace name 'OrderService' could not be found
// Fix: Verify the namespace matches the SUT and the test project references the production project
namespace MyApp.Services.Tests; // Test project must have a ProjectReference to MyApp
```

**Type Mismatch (C#):**
```csharp
// Error: CS0029 cannot implicitly convert type
// Fix: Check return types and parameter types
// Wrong: actualResult.Should().Be("123");  // if actualResult is long
// Correct: actualResult.Should().Be(123L);
```

**Type Mismatch (TypeScript):**
```typescript
// Error: TS2345 Argument of type 'string' is not assignable to parameter of type 'number'
// Fix: Match the interface — read the actual type definitions, don't guess
```

### Verification Checklist

- [ ] Test file is in correct directory
- [ ] Namespace/module structure matches the project layout
- [ ] All using directives / imports are present and correct
- [ ] All dependencies are available
- [ ] No syntax errors
- [ ] Type compatibility is correct
- [ ] Compilation command succeeds

### Example Workflow

```bash
# 1. Create test file
# (using Write tool)

# 2. Run compilation (scoped to the test project)
dotnet build tests/MyApp.Tests/MyApp.Tests.csproj

# 3. If errors, fix and retry
# Error: CS0246 The type or namespace name 'Substitute' could not be found
# Fix: ask the user, then add the NSubstitute package reference (Dependency Guardrail)

# 4. Verify success
dotnet build tests/MyApp.Tests/MyApp.Tests.csproj
# Build succeeded. 0 Warning(s). 0 Error(s).
```

**IMPORTANT:** Never deliver tests that don't compile. Always verify compilation before completing the task.
