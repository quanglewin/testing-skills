---
title: Post-Generation Test Execution Verification
impact: HIGH
impactDescription: ensures generated tests actually pass, not just compile
tags: tests, execution, verification, pass, fail
---

## Post-Generation Test Execution Verification

After tests compile successfully, run them and verify they pass. Tests that compile but fail are not deliverable.

### Process

1. **Run only the generated test class** (not the entire test suite):

| Build System | Command |
|--------------|---------|
| .NET | `dotnet test --filter "FullyQualifiedName~{TestClassName}"` |
| Vitest | `npx vitest run {testFile}` |
| Jest | `npx jest {testFile}` (version-safe) — the pattern flag is `--testPathPattern` on Jest ≤29 but `--testPathPatterns` on Jest ≥30 |
| Python | `python -m pytest {test_file} -v` |
| Go | `go test -run {TestFuncName} ./...` |

2. **Pre-existing tests are protected.** When tests were added to an existing test class/file, the run also executes the team's pre-existing tests. The fix/remove loop below applies ONLY to test methods generated in this run:
   - NEVER delete, rewrite, or disable a pre-existing test method.
   - If a pre-existing test fails and it also fails without your additions (check out / mentally re-run the original state), report the pre-existing failure to the user and continue verifying only your generated tests.
   - If a pre-existing test started failing BECAUSE of your additions (shared state, fixture interference), fix or remove YOUR addition, never the pre-existing test.

3. **If a generated test fails:**
   - Read the failure output carefully
   - Identify the root cause (wrong expected value, incorrect substitute setup, missing stubbing, wrong method behavior assumption)
   - Fix the test — do NOT change the production code
   - Re-run to verify the fix
   - Repeat (max 3 fix attempts per failing test)

4. **If a generated test cannot be fixed after 3 attempts:**
   - Remove the failing test method
   - Add a `// TODO:` comment explaining what was intended and why it failed
   - Inform the user about the removed test
   - **Circuit breaker:** if more than 2 generated tests — or more than 25% of the generated tests — would end up removed, STOP and ask the user how to proceed instead of silently shrinking the delivered coverage. The final summary must list every removed test case against the user-approved list.

### Common Failure Causes and Fixes

**Wrong expected value (C#):**
```csharp
// Failure: Expected actualUser.Name to be "John Doe", but found "John"
// Fix: Read the production code to understand the actual return value
actualUser.Name.Should().Be("John"); // Match actual behavior
```

**Missing substitute stubbing (C#):**
```csharp
// Failure: NullReferenceException — substitute returned null/default
// Fix: Stub the methods the code path actually calls, before invoking the SUT
_repository.FindById("1").Returns(order); // Verify this is on the tested path
```

**Non-virtual member on a substituted class (C#):**
```csharp
// Failure: Returns() has no effect, real code runs instead
// Fix: Substitute the INTERFACE, not the concrete class — NSubstitute cannot
// intercept non-virtual members (see substitute-rules.md)
var repository = Substitute.For<IOrderRepository>();
```

**Unawaited async assertion (TypeScript):**
```typescript
// Failure symptom: test passes even when the code never rejects
// Fix: always await rejects/resolves assertions (see async-testing.md)
await expect(orderService.getOrder('missing')).rejects.toThrow(OrderNotFoundError);
```

**Mock state leaking between tests (TypeScript):**
```typescript
// Failure: test passes alone, fails in the suite (call counts off)
// Fix: restore spies AND clear vi.fn() call history between tests (see mocking-rules.md)
afterEach(() => {
  vi.restoreAllMocks(); // spies created with vi.spyOn()
  vi.clearAllMocks();   // call history of vi.fn() mocks
});
```

### IMPORTANT

- Never deliver tests that fail. Passing tests are the minimum bar.
- Do NOT modify production code to make tests pass. Fix the tests instead.
- If the production code has a bug, the test should document the CURRENT behavior and add a comment noting the suspected bug.
