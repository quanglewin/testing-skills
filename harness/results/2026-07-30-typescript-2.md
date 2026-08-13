# Eval: typescript — 2026-07-30 (run 2)

Fixture: `harness/fixtures/typescript/order-service/` · Target: `src/order-service.ts` · Vitest detection path · Cold-start generation.
**Purpose of run 2:** verify rules after the Java-removal rewrite of the general rules (examples now C#-based).

| Dimension | Result | Gate | Verdict |
|---|---|---|---|
| Compiles | `npx tsc --noEmit` exit 0 (first attempt) | HARD | PASS |
| Passes | `npx vitest run` exit 0 — 15/15 passed (first run, zero fix attempts) | HARD | PASS |
| Case recall | 13/13 golden branches covered = 1.00 | ≥0.90 | PASS |
| Case precision | 0 EXCLUDE violations | 0 | PASS |
| Forbidden patterns | 0 confirmed hits (snapshots/`as any`/`jest.` all 0; one `rejects` grep hit again a false positive — handler attached before timer advance, awaited 6 lines later) | 0 | PASS |
| Conventions | 10/10 applicable = 1.00 — Given-When-Then kept for TS per rules; `actual`/`expected` prefixes; `satisfies`-typed DI mocks; fake timers scoped with `useRealTimers` restore | ≥0.90 | PASS |

**Overall: PASS**

## Comparison with run 1

- 15 cases vs 17: run 2 folded one logging split and one wrap-cause split differently but still covers every golden branch — recall unchanged at 1.00.
- Behavior identical on the hard gates; general-rules rewrite (C#-example-based) did not degrade TS generation.

## Misses

None.

## Notes

- Recurring rubric false positive: the single-line grep for unawaited `rejects` flags the legitimate attach-then-await fake-timer pattern (seen in both runs). Improvement candidate for `/improve-skill`: refine the grep to detect never-awaited expressions instead of same-line `await`.
- Test artifacts removed and fixture verified clean after scoring, per rubric.
