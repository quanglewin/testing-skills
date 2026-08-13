---
title: Mocking Rules for TypeScript Tests
impact: HIGH
impactDescription: ensures meaningful mock verification and prevents module-mock leaks
tags: typescript, javascript, tests, mocking, vitest, jest, dependency-injection
---

## Mocking Rules for TypeScript Tests

Prefer dependency injection over module mocking. Applies to both TypeScript and plain JavaScript. Vitest APIs shown; Jest is identical modulo `vi` → `jest` (see `framework-detection.md`).

### DI-First Hierarchy

1. **Preferred**: pass fake/mock objects via constructor or function parameters — plain objects with `vi.fn()` members
2. **Fallback**: `vi.mock()` / `jest.mock()` module mocking — ONLY for true module-level dependencies that cannot be injected (e.g. a directly imported SDK, `fs`, a date library)

```typescript
// Preferred: dependency injected through the constructor
const orderRepository = {
  findAll: vi.fn().mockReturnValue([]),
  save: vi.fn(),
} satisfies OrderRepository;
const orderService = new OrderService(orderRepository);
```

### FORBIDDEN

- **FORBIDDEN** to mock the module or class under test (`vi.mock('./order-service')` in `order-service.test.ts`).
- **FORBIDDEN** to call `mockReturnValue`/`mockImplementation` on the SUT's own methods — the test then verifies the mock, not the code.

**Incorrect:**

```typescript
it('calculateTotal_validProducts_returnsSum', () => {
  const orderService = new OrderService(orderRepository);
  // Stubbing the SUT's own method — the test no longer tests anything
  vi.spyOn(orderService, 'calculateTotal').mockReturnValue(150);

  expect(orderService.calculateTotal()).toBe(150); // always passes
});
```

### Module-Mock Hoisting Pitfalls

`vi.mock()` calls are hoisted to the top of the file — the factory runs before any `const` in the file is initialized:

**Incorrect:**

```typescript
const fakeSend = vi.fn(); // NOT yet initialized when the factory runs

vi.mock('./email-client', () => ({
  // ReferenceError: Cannot access 'fakeSend' before initialization
  sendEmail: fakeSend,
}));
```

**Correct:**

```typescript
import { sendEmail } from './email-client';

const { fakeSend } = vi.hoisted(() => ({ fakeSend: vi.fn() }));

vi.mock('./email-client', () => ({
  sendEmail: fakeSend,
}));

// vi.mocked() is a type helper that casts the mocked import to its Mock type —
// here sendEmail is the factory's fake
vi.mocked(sendEmail).mockResolvedValue({ delivered: true });
```

### Restore Mocks Between Tests

Unrestored global mocks and spies leak between tests and cause order-dependent failures.

**Incorrect:**

```typescript
it('getTimestamp_fixedClock_returnsIso', () => {
  vi.spyOn(Date, 'now').mockReturnValue(1700000000000);
  // ... no restore — every later test in the run now sees the frozen clock
});
```

**Correct:**

```typescript
afterEach(() => {
  vi.restoreAllMocks(); // restores spies created with vi.spyOn()
  vi.clearAllMocks();   // clears call history of vi.fn() mocks
});
```

Or set it once in config: `test: { restoreMocks: true, clearMocks: true }` (Vitest) / `restoreMocks: true, clearMocks: true` (Jest). If the project config already does this, don't duplicate the `afterEach`.

Note: `vi.restoreAllMocks()` / `jest.restoreAllMocks()` only restores spies created with `spyOn` — it does NOT touch `vi.fn()` / `jest.fn()` mocks (including module-scope `vi.hoisted()` mocks like `fakeSend` above). Whenever mocks live at module or `describe` scope, also call `vi.clearAllMocks()` / `jest.clearAllMocks()` in `afterEach` (or set `clearMocks: true` in config) to clear their call history. `clearAllMocks` clears call history ONLY — implementations stubbed with `mockReturnValue`/`mockResolvedValue` persist; when stubbed implementations must not leak between tests, use `vi.resetAllMocks()` / `jest.resetAllMocks()` (or `resetMocks: true`) and re-stub inside each test.

### Assert What Mocks Were Called WITH

Verify the actual arguments passed to mocks — an existence check hides wrong data. Use `expect.anything()` only for genuinely irrelevant arguments.

**Incorrect:**

```typescript
it('createOrder_validRequest_savesOrder', () => {
  orderService.createOrder({ productId: 'product-1', quantity: 5 });

  // Verifies a call happened, not what was saved
  expect(orderRepository.save).toHaveBeenCalledWith(expect.anything());
});
```

**Correct:**

```typescript
it('createOrder_validRequest_savesCorrectOrder', () => {
  // Given
  const request = { productId: 'product-1', quantity: 5 };

  // When
  orderService.createOrder(request);

  // Then — assert the full expected object...
  expect(orderRepository.save).toHaveBeenCalledWith({
    productId: 'product-1',
    quantity: 5,
    status: 'PENDING',
  });

  // ...or grab the call and assert the relevant fields
  const actualOrder = orderRepository.save.mock.calls[0][0];
  expect(actualOrder.productId).toBe('product-1');
  expect(actualOrder.quantity).toBe(5);
});
```

### Key Points

1. Inject fakes via constructor/params first; `vi.mock()` only for un-injectable module deps
2. `vi.mock()` factories can't reference outer variables — use `vi.hoisted()`
3. `vi.mocked()` for type-safe access to mocked imports
4. `vi.restoreAllMocks()` in `afterEach` (or `restoreMocks` config) — always; add `vi.clearAllMocks()` (or `clearMocks` config) when mocks live at module/`describe` scope — `restoreAllMocks` alone doesn't reset `vi.fn()` mocks
5. Never mock the SUT; assert mock arguments, not just call counts
