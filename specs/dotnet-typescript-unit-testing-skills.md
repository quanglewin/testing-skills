# Spec: .NET and TypeScript/JavaScript Unit-Testing Skills + Verification Harness + Auto-Improvement Loop

**Status:** IMPLEMENTED (2026-08-13)
**Date:** 2026-07-30
**Depends on:** existing `generate-tests` / `generate-test-cases` skills (Java-only today)
**Note:** The "Java-only" baseline referenced in this spec no longer applies — Java rules have since been removed from the repo.

---

## Objective

Extend the repo's test-generation skills from Java-only to three ecosystems:

1. **C# / .NET** unit tests (xUnit + NSubstitute + AwesomeAssertions)
2. **TypeScript / JavaScript** unit tests (Vitest or Jest, detected per project)

And add two new capabilities the repo currently lacks:

3. **Verification harness** — in-repo fixture projects + scoring rubric that measure whether the skills actually produce compiling, passing, rule-compliant tests
4. **Auto-improvement loop** — an on-demand `/improve-skill` skill that runs the harness, diagnoses failures, and proposes rule-file edits as a reviewable PR

**Who is the user?** Engineers who install these skills into .NET or TS/JS projects and run `/generate-tests <target>`.

**Success looks like:** `/generate-tests src/services/order-service.ts` or `/generate-tests Services/OrderService.cs` produces the same quality bar the Java path delivers today — reviewed test cases, compiling code, passing tests, zero forbidden patterns — and the harness proves it repeatably.

### Stack decisions (approved 2026-07-30)

| Decision | Choice | Rationale |
|---|---|---|
| .NET stack | xUnit + NSubstitute + AwesomeAssertions | License-safe: avoids Moq (SponsorLink incident) and FluentAssertions v8+ (commercial license). AwesomeAssertions is the free fork with the same API. |
| TS/JS stack | Detect Jest or Vitest per project | APIs are near-identical; rules written framework-neutral with a detection table + per-framework notes. Matches existing `technology-stack-detection.md` approach. |
| Harness | In-repo `harness/` fixtures + eval | Real compile/pass ground truth beats rubric-only judging. |
| Auto-improve | On-demand `/improve-skill` | Every rule change flows through the existing PR + CODEOWNER gate. CI regression gate deferred (see Open Questions). |

---

## Tech Stack

| Ecosystem | Framework | Mocking | Assertions | Min versions |
|---|---|---|---|---|
| .NET | xUnit 2.9.x (v3 noted in rules, not required) | NSubstitute 5.x | AwesomeAssertions (latest stable) | .NET 8 LTS target for fixtures |
| TypeScript/JS | Vitest 3.x **or** Jest 29/30 (detected) | `vi.fn()` / `jest.fn()`, DI-first | built-in `expect` | Node 20 LTS, TS 5.x for fixtures |

Existing repo conventions carry over unchanged: Given-When-Then, `actual`/`expected` prefixes, INCLUDE/EXCLUDE strategy, `{method}_{state}_{outcome}` naming, existing-test awareness, code-context analysis.

---

## Commands

Harness fixtures (used by eval and by generated-test verification):

```bash
# .NET fixture
dotnet build harness/fixtures/dotnet/OrderService.sln            # compile check
dotnet test harness/fixtures/dotnet --filter "FullyQualifiedName~OrderServiceTests"

# TypeScript fixture
cd harness/fixtures/typescript/order-service
npm ci
npx tsc --noEmit                                                  # compile check
npx vitest run                                                    # test run

# Full eval
# (invoked by the /eval-skills skill; see Harness section)
```

The `compilation-verification.md` and `test-execution-verification.md` rules already list per-ecosystem commands (`dotnet build`, `npx tsc --noEmit`, `npx jest`, etc.) — the new rules reference them rather than duplicating.

---

## Project Structure

New files only (existing structure unchanged):

```
skills/
  generate-tests/
    rules/tests/
      csharp/unit/                     # NEW — mirrors java/unit
        csharp-test-template.md
        substitute-rules.md            # NSubstitute patterns (≈ argument-matching.md)
        json-serialization.md
        logging-rules.md
        domain-service-rules.md
        controller-test-rules.md       # ASP.NET Core controllers
      typescript/unit/                 # NEW — also covers plain JavaScript
        ts-test-template.md
        framework-detection.md         # Jest vs Vitest table + API mapping
        mocking-rules.md
        assertion-rules.md
        async-testing.md
harness/                               # NEW — top level, NOT installed with skills
  fixtures/
    dotnet/
      OrderService.sln
      src/OrderService/                # ~4 classes: service, controller, DTOs, custom exception
      expected-cases.md                # golden test-case list per public method
    typescript/order-service/
      src/                             # service w/ injected deps, async paths, validation
      package.json                     # vitest configured
      expected-cases.md
    java/                              # OPTIONAL later — retrofit existing Java rules
  rubric.md                            # scoring dimensions + weights
  results/                             # eval run outputs, dated, committed
skills/
  eval-skills/SKILL.md                 # NEW — runs harness, produces scorecard
  improve-skill/SKILL.md              # NEW — eval → diagnose → propose rule edits → PR
specs/
  dotnet-typescript-unit-testing-skills.md   # this file
```

**Directory naming:** `csharp/unit` (language name, matching `java/unit` precedent — not `dotnet`). `typescript/unit` covers JS too; rules state this explicitly.

**Charter conflict — must resolve:** `CLAUDE.md` currently says the repo has "no build system, test suite, or application code." The harness adds fixture application code. `CLAUDE.md` gets updated in Task 1 to carve out `harness/` as eval-only code, excluded from skill installation (installers only consume `skills/`).

---

## Code Style

One example per new ecosystem — this is the bar every rule file enforces.

**.NET (xUnit + NSubstitute + AwesomeAssertions):**

```csharp
public class OrderServiceTests
{
    private readonly IOrderRepository _orderRepository = Substitute.For<IOrderRepository>();
    private readonly OrderService _orderService;

    public OrderServiceTests()
    {
        _orderService = new OrderService(_orderRepository);
    }

    [Fact]
    public void CalculateTotal_ValidProducts_ReturnsSum()
    {
        // Arrange
        var products = new List<Product> { new("A", 50.0m), new("B", 100.0m) };
        _orderRepository.FindAll().Returns(products);

        // Act
        decimal actualTotal = _orderService.CalculateTotal();

        // Assert
        decimal expectedTotal = 150.0m;
        actualTotal.Should().Be(expectedTotal);
    }

    [Fact]
    public void CreateOrder_ValidRequest_SavesCorrectOrder()
    {
        // Arrange
        var request = new OrderRequest("product-1", 5);
        Order? capturedOrder = null;
        _orderRepository.Save(Arg.Do<Order>(o => capturedOrder = o));

        // Act
        _orderService.CreateOrder(request);

        // Assert — capture and assert fields, never Arg.Any<Order>() in Received()
        capturedOrder.Should().NotBeNull();
        capturedOrder!.ProductId.Should().Be("product-1");
        capturedOrder.Quantity.Should().Be(5);
    }
}
```

Naming: `Method_State_Outcome` in PascalCase — the C# rendering of the repo's `{method}_{state}_{outcome}` convention. Structure comments: `// Arrange` / `// Act` / `// Assert` (AAA — the .NET convention; equivalent of Given-When-Then elsewhere in this repo).

**TypeScript (Vitest shown; Jest identical modulo `vi`→`jest`):**

```typescript
describe('OrderService', () => {
  describe('calculateTotal', () => {
    it('calculateTotal_validProducts_returnsSum', () => {
      // Given
      const orderRepository = { findAll: vi.fn().mockReturnValue([
        { name: 'A', price: 50 },
        { name: 'B', price: 100 },
      ]) };
      const orderService = new OrderService(orderRepository);

      // When
      const actualTotal = orderService.calculateTotal();

      // Then
      const expectedTotal = 150;
      expect(actualTotal).toBe(expectedTotal);
    });

    it('calculateTotal_emptyList_throwsRangeError', () => {
      const orderRepository = { findAll: vi.fn().mockReturnValue([]) };
      const orderService = new OrderService(orderRepository);

      expect(() => orderService.calculateTotal()).toThrow(RangeError);
    });
  });
});
```

Key conventions encoded in rules:
- DI-first mocking: pass mock objects through constructors/parameters; `vi.mock()`/`jest.mock()` module mocking is the fallback, with hoisting pitfalls documented
- `it()` text keeps `{method}_{state}_{outcome}` for cross-language greppability (see Open Questions)
- No snapshot tests for logic (change-detector rule applied to TS)
- Async: always `await`, use `rejects`/`resolves`, fake timers over real waits

---

## Rule File Specifications

### `csharp/unit/` (6 files, mirroring `java/unit/`)

| File | Encodes | FORBIDDEN patterns |
|---|---|---|
| `csharp-test-template.md` | xUnit structure; constructor = setup (new instance per test — no state leaks); `[Fact]`/`[Theory]` usage; file placement `tests/{Project}.Tests/{Class}Tests.cs`; naming | `WebApplicationFactory`, `Testcontainers`, `[Collection]` for shared mutable state in unit tests (the `@SpringBootTest` equivalents) |
| `substitute-rules.md` | NSubstitute: `.Returns()`, `Received()` verification; capture DTOs via `Arg.Do<T>()` or `Arg.Is<T>(predicate)` and assert fields | `Arg.Any<T>()` for DTO/model args in `Received()`; substituting classes with non-virtual members (silent no-op trap); substituting the SUT |
| `json-serialization.md` | Raw string literals (`"""…"""`) for JSON in stubs/assertions | `JsonSerializer.Serialize` / Newtonsoft `JsonConvert` to build expected values |
| `logging-rules.md` | `FakeLogger` / `FakeLogCollector` from `Microsoft.Extensions.Diagnostics.Testing`; asserting log records | Substituting `ILogger.Log` directly (extension-method trap: `LogInformation` is not interceptable) |
| `domain-service-rules.md` | Constructor injection; what to substitute (repos, clients, I/O) vs real objects (DTOs, entities, mappers); exception assertion via `Invoking(...).Should().Throw<T>()` | DI container (`ServiceProvider`) in unit tests; mocking value objects |
| `controller-test-rules.md` | Direct controller instantiation with substituted services; asserting `ActionResult` types (`OkObjectResult`, `BadRequestResult`, status codes); ModelState validation testing | `WebApplicationFactory`/`TestServer` in *unit* tests (that's integration) |

### `typescript/unit/` (5 files)

| File | Encodes | FORBIDDEN patterns |
|---|---|---|
| `ts-test-template.md` | `describe` per class/module, nested `describe` per method, `it` naming; file placement (`*.test.ts` colocated or `__tests__/` — match project); typed test data | `any`-typed mocks hiding contract drift; one giant `describe` |
| `framework-detection.md` | Detection table: `vitest.config.*`/`vite.config.*` + deps → Vitest; `jest.config.*` → Jest; API mapping table (`vi.fn`↔`jest.fn`, `vi.mock`↔`jest.mock`, timers) | Mixing framework APIs; assuming Jest when project uses Vitest |
| `mocking-rules.md` | DI-first: inject fakes/mock objects; module mocking (`vi.mock`) only for true module-level deps; hoisting rules; `vi.mocked()` for typing; restore mocks between tests | Mocking the SUT; `vi.mock` of the module under test; unrestored global mocks |
| `assertion-rules.md` | `toBe` vs `toEqual` vs `toStrictEqual` decision table; literal expected values; `expect.objectContaining` only for irrelevant-field trimming | Snapshot tests for logic (change-detector); computed expected values; assertions inside conditionals |
| `async-testing.md` | `await expect(...).rejects.toThrow(...)`; returning/awaiting promises; `vi.useFakeTimers()` for time-dependent code; flushing microtasks | Unawaited async assertions (silent pass); `done()` callbacks; real `setTimeout` waits |

All rule files use the existing frontmatter format (`title`, `impact`, `impactDescription`, `tags`) and Incorrect/Correct example pairs.

### Existing files touched

- `skills/generate-tests/SKILL.md` — Step 4 routing gains C# and TS/JS branches; Rules Reference gains both new sections; frontmatter description drops "Supports Java" exclusivity
- `skills/generate-test-cases/SKILL.md` — description update only (general rules already language-neutral)
- `rules/tests/general/technology-stack-detection.md` (both copies, kept in sync) — TS row gains Jest-vs-Vitest detection pointer
- `CLAUDE.md`, `README.md`, `templates/AGENTS-SNIPPET.md` — document new language support + harness carve-out

---

## Verification Harness

### Fixtures

Each fixture is deliberately small (~4 production classes) but covers the branch taxonomy the INCLUDE rules target:

- happy path, validation failure (throw), not-found path, external-failure path
- a private helper reachable only via public API (tests the CRITICAL private-method rule)
- a DTO with required fields (tests code-context-analysis)
- async path + logging call (TS fixture); controller with 400/404 responses (.NET fixture)

Each fixture ships `expected-cases.md`: the golden list of test cases a correct run must produce (derived by hand from the branches), in the repo's standard test-case format.

### Rubric (`harness/rubric.md`)

Per fixture run, scored dimensions:

| Dimension | Measure | Gate |
|---|---|---|
| Compiles | `dotnet build` / `tsc --noEmit` exit 0 | HARD — fail run if not |
| Passes | `dotnet test` / `vitest run` exit 0 | HARD |
| Case recall | generated cases ∩ golden cases / golden | ≥ 0.9 |
| Case precision | no EXCLUDE-rule violations (collection-size dupes, speculative nulls, merged 4xx) | 0 violations |
| Forbidden patterns | grep-able: `WebApplicationFactory`, `Arg.Any<` + `Received`, `JsonSerializer.Serialize` in tests, snapshot for logic, unawaited `rejects` | 0 hits |
| Convention compliance | naming format, Given-When-Then comments, actual/expected prefixes | LLM-judged checklist, ≥ 0.9 |

### `/eval-skills` skill

1. For each fixture: invoke `generate-tests` logic against the fixture target (fresh context, auto-approving the review gate)
2. Run hard gates (compile, pass) via Bash
3. Score recall/precision against `expected-cases.md`; grep forbidden patterns; judge conventions
4. Write `harness/results/{date}-{ecosystem}.md` scorecard; print summary table

---

## Auto-Improvement Loop (`/improve-skill`)

On-demand, human-gated:

```
run /eval-skills
  → collect failures + rule violations
  → classify each: RULE_MISSING | RULE_AMBIGUOUS | RULE_IGNORED | FIXTURE_BUG | EVAL_BUG
  → for RULE_* classes: draft minimal rule-file edit (new Incorrect/Correct pair,
    clarified wording, or new FORBIDDEN entry)
  → apply edits on a branch, re-run affected fixture(s)
  → improved score? keep : revert
  → max 3 iterations
  → open PR: scorecard before/after + per-edit rationale
```

Guardrails:
- **Never auto-merges** — PR + CODEOWNER approval, same as any change
- Never edits fixture production code to make generated tests pass (mirrors the `test-execution-verification.md` rule)
- General-rule edits sync both copies (`generate-test-cases/rules/general/` + `generate-tests/rules/tests/general/`) in the same PR
- FIXTURE_BUG / EVAL_BUG findings are reported, not silently fixed

---

## Testing Strategy

The harness *is* the test suite for this repo. Definition of done for any rules PR: `/eval-skills` scorecard meets every rubric gate on the affected ecosystem's fixture. Results are committed to `harness/results/` so regressions are diffable.

---

## Boundaries

**Always:**
- Keep the two general-rules directories byte-identical when touching general rules
- Update both SKILL.md Rules Reference lists when adding a rule file
- Run `/eval-skills` on the affected ecosystem before merging rule changes
- All changes via PR (branch protection already enforces)

**Ask first:**
- Adding dependencies to fixture projects
- Changing rubric weights/gates
- Changing any general (cross-language) rule
- Adding a new ecosystem beyond these two

**Never:**
- Auto-merge `/improve-skill` output
- Modify fixture production code to make generated tests pass
- Commit generated test files into fixtures (eval runs in temp copies)
- Introduce Moq or FluentAssertions v8+ into fixtures or rule examples

---

## Success Criteria

1. `/generate-tests` on the .NET fixture: compiles, all tests pass, ≥90% golden-case recall, 0 forbidden patterns — reproducibly
2. Same for the TS fixture under **both** Vitest and Jest detection (Jest via a config-swapped fixture variant)
3. 11 new rule files exist, follow existing frontmatter + Incorrect/Correct format, and are listed in `generate-tests/SKILL.md`
4. `/eval-skills` produces a committed scorecard in one command
5. `/improve-skill` demonstrably closes at least one seeded rule gap (validation: intentionally weaken a rule, confirm the loop detects and repairs it) with a reviewable PR
6. `CLAUDE.md`, `README.md`, `AGENTS-SNIPPET.md` updated; general-rule copies still in sync

## Open Questions

1. **TS test naming** — keep `{method}_{state}_{outcome}` in `it()` strings (consistent, greppable) or idiomatic prose (`it('returns sum for valid products')`)? Spec currently says keep the repo format. Maintainer call.
2. **Plain-JS projects** (no TS): rules cover them via the same files with a "skip type-related guidance" note — sufficient, or separate `javascript/unit/`? Spec says same files.
3. **xUnit v3** — rules note it exists; fixtures pin v2.9. Revisit when v3 adoption justifies it.
4. **CI regression gate** (run `/eval-skills` in GitHub Actions on rules PRs) — deferred; requires .NET 8 + Node 20 runners. Natural follow-up once the harness is stable.
5. **Java fixture retrofit** — harness currently specs .NET + TS only; adding a Java fixture would put the existing rules under the same measurement. Recommended follow-up.

---

## Plan (Phase 2 — pending spec approval)

Order and dependencies:

```
T1 (charter/docs) ──► T2 (.NET rules) ──┬─► T4 (SKILL.md wiring) ──► T5 (.NET fixture) ──► T7 (eval skill) ──► T9 (improve skill) ──► T10 (validation)
                      T3 (TS rules)  ───┘                            T6 (TS fixture)  ───┘
```

T2∥T3 and T5∥T6 parallelize. Riskiest-first: eval skill (T7) design is validated on the .NET fixture before the improve loop (T9) builds on it.

**Risks:**
- *Eval nondeterminism* (LLM-judged convention score varies) → hard gates are deterministic; LLM judge only scores the soft dimension, threshold 0.9 not 1.0
- *Fixture drift toward triviality* (fixtures too easy → rules look better than they are) → fixtures must cover every INCLUDE-taxonomy branch; golden lists reviewed by maintainer
- *Vitest/Jest API drift* → framework-detection rule owns the mapping table; single place to update
- *AwesomeAssertions API divergence from FluentAssertions docs* → rule examples tested by fixture compilation, not copied from FA docs

## Tasks (Phase 3 — pending plan approval)

- [ ] **T1: Charter + docs prep**
  - Acceptance: `CLAUDE.md` documents `harness/` carve-out; `specs/` referenced
  - Verify: read-through; no contradiction with "skills-only" claims
  - Files: `CLAUDE.md`, this spec
- [ ] **T2: C# rule files (6)**
  - Acceptance: 6 files in `rules/tests/csharp/unit/`, existing frontmatter format, Incorrect/Correct pairs, FORBIDDEN sections per table above
  - Verify: format lint vs existing java rules; all code snippets compile mentally against xUnit 2.9/NSubstitute 5 APIs
  - Files: 6 new
- [ ] **T3: TS rule files (5)**
  - Acceptance: 5 files in `rules/tests/typescript/unit/`, framework-detection table covers Vitest 3 + Jest 29/30
  - Verify: same as T2
  - Files: 5 new
- [ ] **T4: SKILL.md wiring**
  - Acceptance: Step 4 routing (controller/service per language), Rules Reference complete, descriptions updated
  - Verify: every new rule file appears exactly once in the reference list
  - Files: 2 SKILL.md + 2 copies of `technology-stack-detection.md` (sync!)
- [ ] **T5: .NET fixture + golden cases**
  - Acceptance: solution builds clean on .NET 8; covers full branch taxonomy; `expected-cases.md` hand-derived
  - Verify: `dotnet build` exit 0
  - Files: ~8 new under `harness/fixtures/dotnet/`
- [ ] **T6: TS fixture + golden cases**
  - Acceptance: `tsc --noEmit` clean; vitest configured; jest-variant config included
  - Verify: `npx tsc --noEmit` exit 0
  - Files: ~7 new under `harness/fixtures/typescript/`
- [ ] **T7: Rubric + `/eval-skills`**
  - Acceptance: one command → scorecard file with all six dimensions
  - Verify: run against both fixtures with current (pre-improvement) rules; scorecard commits
  - Files: `harness/rubric.md`, `skills/eval-skills/SKILL.md`
- [ ] **T8: README + AGENTS-SNIPPET + BEST_PRACTICES updates**
  - Acceptance: language support matrix updated everywhere
  - Verify: grep for "Java" exclusivity claims → none remain
  - Files: 3
- [ ] **T9: `/improve-skill`**
  - Acceptance: classify→edit→re-eval→PR loop per spec; guardrails encoded in SKILL.md
  - Verify: dry run produces a coherent PR draft
  - Files: `skills/improve-skill/SKILL.md`
- [ ] **T10: End-to-end validation**
  - Acceptance: all six Success Criteria pass, incl. seeded-gap repair test
  - Verify: `/eval-skills` green on both ecosystems; seeded weakening of `substitute-rules.md` detected and repaired by `/improve-skill`
  - Files: none (validation only)
