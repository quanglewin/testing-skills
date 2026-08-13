# Eval: typescript — 2026-08-13

Fixture: `harness/fixtures/typescript/order-service/` · Target: `src/order-service.ts` · Cold-start generation (golden list and rubric withheld from the generating agent). Run against the enterprise-hardened skill (Step 0 target validation, Boundaries, dependency guardrail, pre-existing-test protection, scoped verification).

| Dimension | Result | Gate | Verdict |
|---|---|---|---|
| Compiles | `npx tsc --noEmit` exit 0 (baseline verified clean before generation) | HARD | PASS |
| Passes | `npx vitest run tests/order-service.test.ts` exit 0 — 15/15 passed | HARD | PASS |
| Case recall | 13/13 golden branches covered = 1.00 | ≥0.90 | PASS |
| Case precision | 0 EXCLUDE violations | 0 | PASS |
| Forbidden patterns | 0 hits (snapshots, done(), `as any` on mocks, jest-API mixing, real setTimeout: all 0; see Notes for the judged `.rejects` grep hit) | 0 | PASS |
| Conventions | 9/9 applicable checklist items = 1.00 | ≥0.90 | PASS |

**Overall: PASS**

## Recall detail

All 13 golden cases matched: both `#applyDiscount` branches through `createOrder` inputs (boundary total exactly 100 pinned), validation guards with save-never-called assertions, gateway success/declined/reject-with-`cause`, found/not-found, and all four `retryPayment` cases including the fake-timer delay cases (`vi.advanceTimersByTimeAsync(1000)`, exact charge-call counts).

Extra generated cases beyond the golden list: `createOrder_validRequest_returnsSavedOrder` and `createOrder_validRequest_logsOrderCreation` (return-passthrough and logging split out of golden case 3's combined Then). Judged distinct observable behaviors per `test-behaviors-not-methods.md` and the 2026-07-30 precedent — not EXCLUDE violations. Flag for maintainer: the golden list's scoring note prefers logging assertions inside the owning case's Then rather than as separate cases; the two sources disagree slightly.

## Misses

None.

## Notes

- Forbidden-pattern grep flagged lines 306–307 (`expect(actualPromise).rejects...` without `await` on the same statement). Judged legitimate: the attach-before-advance pattern stores the rejection assertions, advances fake timers, then awaits both assertion promises (lines 313–314) — required to avoid an unhandled rejection with fake timers; not a floating assertion.
- Framework detection correct: Vitest chosen from root `vitest.config.ts` + devDependencies; explicit `import { ... } from 'vitest'` since `globals: true` is not set; the `jest.variant/` directory correctly ignored as non-root.
- Given/When/Then comments throughout; `actual`/`expected` prefixes; typed mocks via `satisfies` (no `as any`); builders (`createOrderRequest`, `createTestOrder`); DTO capture via `save.mock.calls[0][0]` with field assertions; logging asserted through the injected logger fake.
- Fake timers scoped to the `retryPayment` describe block with `beforeEach`/`afterEach` setup/teardown, per `async-testing.md`.
- New guardrails exercised: Step 0 resolved the target; baseline `tsc --noEmit` run before generation; no packages installed (deps pre-existing); Step 5 scope check confirmed the only change was the new `tests/order-service.test.ts`.
- Fixture integrity: nothing under `src/` modified; fixture reset to HEAD after scoring.
