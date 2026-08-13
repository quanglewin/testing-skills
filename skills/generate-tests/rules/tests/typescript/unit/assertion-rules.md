---
title: Assertion Rules for TypeScript Tests
impact: HIGH
impactDescription: ensures assertions verify correctness instead of silently passing or detecting mere change
tags: typescript, javascript, tests, assertions, expect, snapshots
---

## Assertion Rules for TypeScript Tests

Choose the right matcher and keep expected values literal. Applies to both TypeScript and plain JavaScript. `expect` API is identical in Vitest and Jest.

### Matcher Decision Table

| Matcher | Comparison | Use for |
|---|---|---|
| `toBe` | `Object.is` (identity) | primitives; asserting the same object reference |
| `toEqual` | deep equality, ignores `undefined` properties | most objects/arrays |
| `toStrictEqual` | deep equality + `undefined` properties + class/prototype must match | DTOs where shape and class matter exactly |

```typescript
// toBe — primitives and references
expect(actualTotal).toBe(150);
expect(actualInstance).toBe(sharedSingleton); // same reference

// toEqual — deep equality; note: ignores undefined props
expect(actualOrder).toEqual({ productId: 'product-1', quantity: 5 });
expect({ a: 1, b: undefined }).toEqual({ a: 1 }); // passes!

// toStrictEqual — undefined props and class matter
expect({ a: 1, b: undefined }).toStrictEqual({ a: 1 }); // fails — b differs
expect(new Order('product-1')).toStrictEqual(new Order('product-1')); // class checked
```

`expect(actualObject).toBe(expectedObject)` on two separately-built objects always fails — use `toEqual`/`toStrictEqual` for structural comparison.

### Literal Expected Values

No computed expectations — no concatenation, arithmetic, or calls to the SUT's own logic in the expected value (see `no-logic-in-tests.md`).

**Incorrect:**

```typescript
expect(actualTotal).toBe(price * quantity + tax);
expect(actualGreeting).toBe(`Hello, ${userName}!`);
```

**Correct:**

```typescript
const expectedTotal = 115; // 100 * 1 + 15 tax, pre-calculated
expect(actualTotal).toBe(expectedTotal);
expect(actualGreeting).toBe('Hello, John!');
```

### objectContaining / arrayContaining

Use `expect.objectContaining` / `expect.arrayContaining` only to trim genuinely irrelevant fields (timestamps, generated IDs) — not as a shortcut to avoid writing the full expectation.

```typescript
// OK — createdAt is nondeterministic and irrelevant to this test
expect(actualOrder).toEqual(expect.objectContaining({
  productId: 'product-1',
  quantity: 5,
}));
```

If every field is relevant, assert the whole object with `toEqual`.

### Make Values Deterministic Instead of Tolerating Them

When a "nondeterministic" value actually matters to the behavior under test, control it instead of loosening the assertion with `expect.objectContaining` / `expect.any(...)`:

- **Time**: freeze the clock with `vi.setSystemTime(...)` inside fake timers (Jest: `jest.setSystemTime(...)` after `jest.useFakeTimers()`)
- **Env vars**: `vi.stubEnv('API_URL', 'https://test.example')` + `vi.unstubAllEnvs()` in `afterEach` (Jest: snapshot/restore `process.env` in `beforeEach`/`afterEach`)
- **Randomness**: `vi.spyOn(Math, 'random').mockReturnValue(0.5)`, `vi.spyOn(crypto, 'randomUUID').mockReturnValue('00000000-0000-0000-0000-000000000001')` — restore after each test

```typescript
// createdAt matters here — freeze time and assert the exact value
beforeEach(() => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date('2024-01-15T00:00:00Z'));
});

afterEach(() => {
  vi.useRealTimers();
});

it('createOrder_validRequest_stampsCreationTime', () => {
  const actualOrder = orderService.createOrder({ productId: 'product-1', quantity: 5 });

  expect(actualOrder).toEqual({
    productId: 'product-1',
    quantity: 5,
    createdAt: new Date('2024-01-15T00:00:00Z'),
  });
});
```

Prefer controlling the value over loose matchers like `expect.objectContaining` whenever the value matters.

### FORBIDDEN: Snapshot Tests for Logic

- **FORBIDDEN** to use `toMatchSnapshot()` / `toMatchInlineSnapshot()` to verify logic. Snapshots are change-detector tests: they are brittle, fail on any refactor, and verify nothing about correctness — a wrong snapshot recorded once passes forever.

**Incorrect:**

```typescript
it('calculateInvoice_validOrder_returnsInvoice', () => {
  const actualInvoice = invoiceService.calculateInvoice(order);
  // Detects change, not correctness — and `--update` blesses any bug
  expect(actualInvoice).toMatchSnapshot();
});
```

**Correct:**

```typescript
it('calculateInvoice_validOrder_returnsCorrectTotals', () => {
  const actualInvoice = invoiceService.calculateInvoice(order);

  expect(actualInvoice.subtotal).toBe(100);
  expect(actualInvoice.tax).toBe(15);
  expect(actualInvoice.total).toBe(115);
});
```

Snapshots are acceptable only for genuinely presentational output (e.g. rendered markup), and even then prefer explicit assertions on the parts that matter.

### FORBIDDEN: Assertions Inside Conditionals or try-catch

An assertion inside an `if` or `catch` passes silently when the branch is skipped.

**Incorrect:**

```typescript
it('parse_invalidInput_throwsValidationError', () => {
  try {
    parser.parse('not-json');
  } catch (error) {
    // If parse() stops throwing, this branch is skipped and the test passes
    expect(error).toBeInstanceOf(ValidationError);
  }
});
```

**Correct:**

```typescript
it('parse_invalidInput_throwsValidationError', () => {
  expect(() => parser.parse('not-json')).toThrow(ValidationError);
});

// Async: use rejects (see async-testing.md)
it('fetchOrder_missingId_rejectsWithNotFoundError', async () => {
  await expect(orderService.fetchOrder('missing')).rejects.toThrow(NotFoundError);
});
```

If a catch-based structure is truly unavoidable, guard it with `expect.assertions(1)` at the top of the test so a skipped branch fails the test.

### Key Points

1. `toBe` for primitives/references, `toEqual` for objects, `toStrictEqual` when `undefined` props or class identity matter
2. Literal expected values — no computed expectations
3. `objectContaining` only to trim irrelevant fields; if the value matters, make it deterministic (freeze time, stub env vars/randomness)
4. No snapshots for logic — explicit assertions
5. No assertions inside conditionals/try-catch — use `toThrow`/`rejects` or `expect.assertions(n)`
