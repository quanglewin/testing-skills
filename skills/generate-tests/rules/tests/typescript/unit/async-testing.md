---
title: Async Testing Rules
impact: HIGH
impactDescription: prevents silently passing tests from unawaited promises and flaky real-timer waits
tags: typescript, javascript, tests, async, promises, timers, vitest, jest
---

## Async Testing Rules

Always await async expectations. Applies to both TypeScript and plain JavaScript. Vitest APIs shown; Jest is identical modulo `vi` → `jest` (see `framework-detection.md`).

### CRITICAL: Unawaited `rejects` Silently Passes

`expect(promise).rejects.toThrow()` returns a promise. Without `await`, the test finishes before the assertion runs — a floating promise. The test passes even when the code never rejects.

**Incorrect:**

```typescript
it('fetchOrder_missingId_throwsNotFoundError', () => {
  // No await — assertion floats, test ALWAYS passes
  expect(orderService.fetchOrder('missing')).rejects.toThrow(NotFoundError);
});
```

**Correct:**

```typescript
it('fetchOrder_missingId_throwsNotFoundError', async () => {
  // Given
  orderRepository.findById.mockResolvedValue(undefined);

  // When-Then — await the rejection assertion, match the specific error
  await expect(orderService.fetchOrder('missing')).rejects.toThrow(NotFoundError);
});
```

Always `await` (or `return`) `rejects`/`resolves` assertions, and match a specific error type or message — a bare `.rejects.toThrow()` passes on any failure.

### Async Success Paths

Await the call and assert on the result:

```typescript
it('fetchOrder_existingId_returnsOrder', async () => {
  // Given
  orderRepository.findById.mockResolvedValue({ id: 'order-1', quantity: 5 });

  // When
  const actualOrder = await orderService.fetchOrder('order-1');

  // Then
  const expectedOrder = { id: 'order-1', quantity: 5 };
  expect(actualOrder).toEqual(expectedOrder);
});
```

`await expect(promise).resolves.toEqual(...)` is equivalent; prefer `const actualResult = await ...` for readability with multiple assertions.

### Testing That an Async Function Does NOT Reject

Just await it — the test fails automatically on rejection. No try-catch, no `resolves.not.toThrow` gymnastics:

```typescript
it('deleteOrder_alreadyDeleted_completesWithoutError', async () => {
  await orderService.deleteOrder('gone-id');
});
```

Note: a bare `await` has zero `expect()` calls, which fails eslint's `expect-expect` rule (common in enterprise configs). When the project lints with `expect-expect`, use `await expect(orderService.deleteOrder('gone-id')).resolves.toBeUndefined();` — or assert an observable side effect — instead of the bare await.

### FORBIDDEN

- **FORBIDDEN** to use `done()` callbacks — deprecated pattern; a thrown assertion inside the callback is swallowed and the test times out instead of reporting the failure.
- **FORBIDDEN** to use real timers or sleeps (`await new Promise(r => setTimeout(r, 1000))`) — slow and flaky. Use fake timers.

**Incorrect:**

```typescript
it('retry_failsTwice_succeedsOnThirdAttempt', (done) => {
  retryService.run().then((result) => {
    expect(result).toBe('ok'); // failure here = swallowed, test just times out
    done();
  });
});

it('debounce_waits_beforeCalling', async () => {
  debounced();
  await new Promise((resolve) => setTimeout(resolve, 1000)); // real 1s wait
  expect(callback).toHaveBeenCalled();
});
```

**Correct:**

```typescript
describe('debounce', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('debounce_delayElapsed_invokesCallback', () => {
    // Given
    const callback = vi.fn();
    const debounced = debounce(callback, 1000);

    // When
    debounced();
    vi.advanceTimersByTime(1000);

    // Then
    expect(callback).toHaveBeenCalledTimes(1);
  });
});
```

Always restore with `vi.useRealTimers()` in `afterEach` — leaked fake timers break unrelated tests.

### Microtask Flushing with Fake Timers

When timer callbacks chain promises (e.g. `setTimeout` firing an async function), synchronous `advanceTimersByTime` fires the timer but doesn't flush the promise chain. Use the async variants:

```typescript
describe('pollStatus', () => {
  beforeEach(() => {
    vi.useFakeTimers(); // required — advanceTimersByTimeAsync throws "Timers are not mocked" otherwise
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('pollStatus_becomesReady_resolvesWithStatus', async () => {
    // Given
    const actualPromise = poller.pollStatus(); // internally: setTimeout + await fetch

    // When — advances timers AND awaits resulting microtasks
    await vi.advanceTimersByTimeAsync(5000);
    // or run everything queued: await vi.runAllTimersAsync();

    // Then
    await expect(actualPromise).resolves.toBe('READY');
  });
});
```

### Key Points

1. Every `rejects`/`resolves` assertion must be awaited — unawaited = silent pass
2. Match specific error types/messages in `rejects.toThrow(...)`
3. Success paths: `const actualResult = await service.method()`
4. "Does not reject" = just await it
5. No `done()` callbacks; no real timers — fake timers + `advanceTimersByTime[Async]`, restored in `afterEach`
