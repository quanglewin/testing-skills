---
title: Vitest vs Jest Framework Detection
impact: HIGH
impactDescription: prevents generating tests for the wrong framework that fail to run
tags: typescript, javascript, tests, vitest, jest, detection, framework
---

## Vitest vs Jest Framework Detection

Detect which framework the project uses BEFORE writing any test code. Applies to both TypeScript and plain JavaScript projects. Never assume Jest by default.

### Detection Table

| Signal | Framework |
|---|---|
| `vitest.config.*` exists (`.ts` / `.js` / `.mts` / `.cts` / `.mjs` / `.cjs`) | Vitest |
| `vite.config.*` contains a `test` key | Vitest |
| `vitest` in `devDependencies` | Vitest |
| `jest.config.*` exists (`.js` / `.ts` / `.mjs` / `.cjs` / `.cts` / `.json`) | Jest |
| `"jest"` key in `package.json` | Jest |
| `jest` in `devDependencies` | Jest |

**If both are present** (e.g. during a migration): prefer the framework that has a config file. If both have config files or the signals are still ambiguous, ask the user which framework to target.

**If neither is present**: STOP and ask the user which framework to target — and whether adding it as a `devDependency` is approved. Never silently pick one.

### API Mapping Table

The APIs are near-identical; only the namespace differs:

| Vitest | Jest |
|---|---|
| `vi.fn()` | `jest.fn()` |
| `vi.mock()` | `jest.mock()` |
| `vi.spyOn()` | `jest.spyOn()` |
| `vi.useFakeTimers()` / `vi.useRealTimers()` | `jest.useFakeTimers()` / `jest.useRealTimers()` |
| `vi.advanceTimersByTime()` | `jest.advanceTimersByTime()` |
| `vi.mocked()` | `jest.mocked()` |
| `vi.restoreAllMocks()` | `jest.restoreAllMocks()` |
| `import { describe, it, expect, vi } from 'vitest'` | globals, or `import { describe, it, expect, jest } from '@jest/globals'` |

### FORBIDDEN

- **FORBIDDEN** to mix framework APIs in one test file (`vi.fn()` alongside `jest.mock()`).
- **FORBIDDEN** to assume Jest when the project uses Vitest (or vice versa).

**Incorrect:**

```typescript
// Project has vitest.config.ts, but test uses Jest APIs — fails at runtime
describe('OrderService', () => {
  it('calculateTotal_validProducts_returnsSum', () => {
    // ReferenceError: jest is not defined (under Vitest)
    const orderRepository = { findAll: jest.fn().mockReturnValue([]) };
    // ...
  });
});
```

**Correct:**

```typescript
// Project has vitest.config.ts → use Vitest imports and vi.* APIs
import { describe, it, expect, vi } from 'vitest';

describe('OrderService', () => {
  it('calculateTotal_validProducts_returnsSum', () => {
    const orderRepository = { findAll: vi.fn().mockReturnValue([]) };
    // ...
  });
});
```

### Imports and Globals

- **Vitest**: `describe`, `it`, `expect`, `vi` must be imported from `'vitest'` — unless the project sets `globals: true` in `vitest.config.ts` (`test: { globals: true }`). Check the config; if `globals: true`, match the project's existing style (existing tests usually omit imports then).
- **Jest**: `describe`, `it`, `expect`, `jest` are globals by default. Projects using `@jest/globals` import them explicitly — match existing tests.

### ESM vs CJS Note

`vi.mock()` / `jest.mock()` hoisting behaves differently across module systems:

- **Vitest** is ESM-native; `vi.mock()` calls are hoisted by a transform, and mock factories must not reference outer variables (use `vi.hoisted()` — see `mocking-rules.md`).
- **Jest** with CJS hoists `jest.mock()` via babel-jest; with ESM (`--experimental-vm-modules`), `jest.mock()` does not hoist — `jest.unstable_mockModule()` plus dynamic `import()` is required. If the project is Jest+ESM, match its existing module-mocking pattern.

### Key Points

1. Detect the framework from config files and `devDependencies` before writing tests
2. Both present → prefer the one with a config file; still ambiguous → ask the user; neither present → STOP and ask which framework to target (and whether adding it as a `devDependency` is approved)
3. Use one framework's API consistently; the mapping table converts between them
4. Check `globals: true` (Vitest) or `@jest/globals` usage (Jest) to match import style
