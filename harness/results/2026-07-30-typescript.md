# Eval: typescript — 2026-07-30

Fixture: `harness/fixtures/typescript/order-service/` · Target: `src/order-service.ts` · Vitest detection path · Cold-start generation (golden list and rubric withheld from the generating agent).

| Dimension | Result | Gate | Verdict |
|---|---|---|---|
| Compiles | `npx tsc --noEmit` exit 0 | HARD | PASS |
| Passes | `npx vitest run` exit 0 — 17/17 passed (first run, no fix attempts) | HARD | PASS |
| Case recall | 13/13 golden branches covered = 1.00 | ≥0.90 | PASS |
| Case precision | 0 EXCLUDE violations | 0 | PASS |
| Forbidden patterns | 0 confirmed hits (snapshots, `as any`, `jest.` mixing, `done()`: all 0; one `rejects` grep hit was a false positive — see Notes) | 0 | PASS |
| Conventions | 10/10 applicable checklist items = 1.00 | ≥0.90 | PASS |

**Overall: PASS**

## Recall detail

All 13 golden cases matched, including both private `#applyDiscount` branches via `createOrder` inputs (boundary total=100 pinned), the gateway-rejection cause-wrapping branch, and all 4 `retryPayment` cases (fake-timer retry after 1000 ms; exhaustion). Generated 17 cases total: the 4 extras split logging side effects into separate behavior tests (e.g. `processPayment_chargeDeclined_logsPaymentError`) — endorsed by `test-behaviors-not-methods.md`, not duplicates.

## Misses

None.

## Notes

- Framework detection correct: Vitest chosen (config file + devDependency), explicit imports (no `globals: true` assumed).
- DI-first mocking throughout: typed `vi.fn<Interface['method']>()` under `satisfies` checks — zero `as any`. `vi.restoreAllMocks()` + `vi.useRealTimers()` in `afterEach`.
- False-positive grep: `const actualRejection = expect(p).rejects.toBeInstanceOf(...)` (test file line ~318) attaches the rejection handler before advancing fake timers and awaits it two lines later — correct pattern for timer-driven rejections, not a floating assertion. Judged OK. Consider refining the rubric grep to look for never-awaited reject expressions.
- Placement: `tests/` directory (fixture tsconfig includes it; no colocated precedent existed).
- esbuild allow-scripts quirk did not materialize — vitest ran without rebuild.
- Test artifacts removed and fixture reset to HEAD after scoring, per rubric.
