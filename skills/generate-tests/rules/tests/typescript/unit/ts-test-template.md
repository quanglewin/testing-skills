---
title: TypeScript Test Template
impact: HIGH
impactDescription: ensures consistent test structure and typed test data
tags: typescript, javascript, tests, template, structure, vitest, jest
---

## TypeScript Test Template

Use `describe`/`it` with consistent structure. Applies to both TypeScript and plain JavaScript projects (for plain JS, use the same structure minus type annotations).

### Structure Rules

- One top-level `describe` per class/module under test
- One nested `describe` per method/function
- `it` names follow `{method}_{state}_{outcome}` (matches the repo-wide naming convention)
- Given-When-Then comments; `actual`/`expected` variable prefixes

### FORBIDDEN

- **FORBIDDEN** to use one giant `describe` with a flat list of `it` blocks for a multi-method class.
- **FORBIDDEN** to use `any`-typed mocks or fixtures — they hide contract drift when the real interface changes.

**Incorrect:**

```typescript
// One flat describe, any-typed mock hides contract drift
describe('OrderService', () => {
  it('calculateTotal_validProducts_returnsSum', () => {
    const orderRepository = { findAll: vi.fn().mockReturnValue([]) } as any;
    // If OrderRepository.findAll is renamed, this test still compiles — silently broken
    const orderService = new OrderService(orderRepository);
    // ...
  });

  it('createOrder_validRequest_savesOrder', () => {
    // ...mixed in the same flat list as calculateTotal tests
  });
});
```

**Correct:**

```typescript
import { describe, it, expect, vi } from 'vitest';
import { OrderService } from './order-service';
import type { OrderRepository } from './order-repository';

describe('OrderService', () => {
  describe('calculateTotal', () => {
    it('calculateTotal_validProducts_returnsSum', () => {
      // Given
      const orderRepository = {
        findAll: vi.fn().mockReturnValue([
          { name: 'A', price: 50 },
          { name: 'B', price: 100 },
        ]),
      } satisfies OrderRepository;
      const orderService = new OrderService(orderRepository);

      // When
      const actualTotal = orderService.calculateTotal();

      // Then
      const expectedTotal = 150;
      expect(actualTotal).toBe(expectedTotal);
    });

    it('calculateTotal_emptyList_throwsRangeError', () => {
      // Given
      const orderRepository = { findAll: vi.fn().mockReturnValue([]) } satisfies OrderRepository;
      const orderService = new OrderService(orderRepository);

      // When-Then
      expect(() => orderService.calculateTotal()).toThrow(RangeError);
    });
  });

  describe('createOrder', () => {
    it('createOrder_validRequest_savesOrder', () => {
      // Given-When-Then
    });
  });
});
```

Jest note: same template with `jest.fn()` instead of `vi.fn()`; Jest provides `describe`/`it`/`expect`/`jest` as globals (or import from `@jest/globals`). See `framework-detection.md`.

### Basic Template Structure

```typescript
import { describe, it, expect, vi } from 'vitest'; // Jest: globals or @jest/globals
import { TestedClass } from './{tested-file}';

describe('{TestedClassName}', () => {
  describe('{testedMethod}', () => {
    it('{testedMethod}_{givenState}_{expectedOutcome}', () => {
      // Given
      // When
      // Then
    });

    it('{testedMethod}_anotherState_expectedResult', () => {
      // Given-When-Then
    });
  });
});
```

### File Placement

Match the project's existing convention (see `existing-test-awareness.md`):

- **Colocated**: `{name}.test.ts` next to `{name}.ts` (e.g. `src/order-service.test.ts`)
- **Separate dir**: `__tests__/{name}.test.ts` beside the source directory

Detect by looking at where existing tests live. If no tests exist, prefer colocated `{name}.test.ts`. Use `.test.tsx` for React component files, `.test.js` for plain-JS projects.

### Typed Test Data

- Type mock objects against the real interface: `satisfies OrderRepository` or an explicit typed constant (`const repo: OrderRepository = {...}`)
- Type fixtures against the real DTO/entity types so the compiler catches contract drift
- Plain-JS projects: same structure without annotations; keep fixture shapes matching the real objects

### Key Points

1. Nested `describe` per method — one top-level `describe` per class/module
2. `it('{method}_{state}_{outcome}')` naming, Given-When-Then comments
3. `actual`/`expected` prefixes for result and expectation variables
4. Typed mocks and fixtures — never `as any`
5. Match the project's test file placement convention
