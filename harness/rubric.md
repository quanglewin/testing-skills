# Skill Evaluation Rubric

Scoring criteria for a single evaluation run of `/generate-tests` against one harness fixture.
Used by the `/eval-skills` skill. A run's scorecard reports every dimension; HARD gates
fail the run outright.

## Dimensions

| # | Dimension | How measured | Gate |
|---|-----------|--------------|------|
| 1 | Compiles | .NET: `dotnet build` exit 0 with generated test project included. TS: `npx tsc --noEmit` exit 0 with generated test files included. | **HARD** — run fails if not |
| 2 | Passes | .NET: `dotnet test` exit 0. TS: `npx vitest run` (or `npx jest`) exit 0. | **HARD** |
| 3 | Case recall | `matched golden cases / total golden cases`, where a generated case matches a golden case if it covers the same code branch with the same expected outcome (name similarity is a hint, branch coverage is the criterion). | ≥ 0.90 |
| 4 | Case precision | Count of EXCLUDE-rule violations in the generated case list: collection-size duplicate scenarios, speculative cases, null-argument tests on non-nullable params, merged HTTP status codes ("4xx"), duplicate same-outcome scenarios. | 0 violations |
| 5 | Forbidden patterns | Grep of generated test code (per-ecosystem list below). | 0 hits |
| 6 | Convention compliance | Checklist judged by the evaluating agent reading the generated tests (list below). Score = passed items / total items. | ≥ 0.90 |

**Overall verdict:** PASS only if all six gates met.

## Forbidden-pattern greps

### .NET (`csharp`)

| Pattern | Why |
|---|---|
| `WebApplicationFactory` | Integration testing in a unit test |
| `TestServer` | Same |
| `Testcontainers` | Same |
| `Arg.Any<` in the same statement/chain as `.Received(` | DTO/model args must be captured and asserted (`substitute-rules.md`) — allowed only for explicitly irrelevant args; flag for judge review rather than auto-fail if ambiguous |
| `JsonSerializer.Serialize` / `JsonConvert.SerializeObject` | Expected JSON must be literal (`json-serialization.md`) |
| `new ServiceCollection()` / `BuildServiceProvider` | DI container in unit test |

### TypeScript/JavaScript (`typescript`)

| Pattern | Why |
|---|---|
| `toMatchSnapshot` / `toMatchInlineSnapshot` | Change-detector test (`assertion-rules.md`) |
| `expect(` + `.rejects` not preceded by `await ` or `return ` on same statement | Floating async assertion — silent pass (`async-testing.md`) |
| `done()` callback parameter in `it(`/`test(` | Deprecated error-swallowing pattern |
| `as any` applied to a mock/stub object | Untyped mock hides contract drift (`ts-test-template.md`) |
| `jest.` API in a Vitest project or `vi.` in a Jest project | Framework mixing (`framework-detection.md`) |
| `setTimeout` with real delay inside a test body | Real waits — must use fake timers |

## Convention checklist (dimension 6)

- [ ] Every test name follows `{method}_{state}_{outcome}` (PascalCase `Method_State_Outcome` for C#)
- [ ] Structure comments present: `// Arrange` / `// Act` / `// Assert` for C# (AAA — .NET convention); `// Given` / `// When` / `// Then` for TS/JS
- [ ] `actual`/`expected` variable prefixes used where a comparison is made
- [ ] One scenario per test (no multi-When tests, no state changes between assertion groups)
- [ ] Expected values are literals — no computation, concatenation, or loops in tests
- [ ] Mock/substitute verification captures DTO fields rather than blanket `any`-matching (where DTOs are verified)
- [ ] Test data via helpers/builders where setup exceeds ~5 lines of irrelevant detail
- [ ] Existing project conventions matched (only applicable when fixture gains pre-existing tests)
- [ ] No production-code modifications made by the run (git diff of fixture `src/` must be empty)
- [ ] Logging assertions use the ecosystem's sanctioned mechanism (FakeLogger / injected logger fake)

## Scorecard format

Written to `harness/results/{YYYY-MM-DD}-{ecosystem}.md`:

```markdown
# Eval: {ecosystem} — {date}

| Dimension | Result | Gate | Verdict |
|---|---|---|---|
| Compiles | exit 0 | HARD | PASS |
| Passes | exit 0 (14/14 tests) | HARD | PASS |
| Case recall | 13/14 = 0.93 | ≥0.90 | PASS |
| Case precision | 0 violations | 0 | PASS |
| Forbidden patterns | 0 hits | 0 | PASS |
| Conventions | 9/10 = 0.90 | ≥0.90 | PASS |

**Overall: PASS**

## Misses
- Golden case `ProcessPayment_GatewayTimeout_ThrowsPaymentFailedException` not generated (recall miss)

## Notes
- {anything the judge flagged for human attention}
```

## Rules for the evaluator

- Never edit fixture production code (`src/`) — a dirty fixture diff fails the run.
- Generated tests are written into the fixture's test location for the run, then deleted
  (or the fixture reset via `git checkout -- harness/fixtures/`) after the scorecard is recorded.
- Ambiguous forbidden-pattern hits (e.g. a legitimately irrelevant `Arg.Any`) go to the
  convention judge with a note — do not silently pass or fail them.
- Record every run, including failing ones. Failing scorecards are the input to `/improve-skill`.
