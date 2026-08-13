# Super Comprehensive Unit Test & Skill Development Best Practices

# Part 1: Building Skills for Claude & AI Agents

Based on Anthropic's 'The Complete Guide to Building Skills for Claude' and Vercel's AGENTS.md research.

## 1.1. Why AGENTS.md Matters
According to Vercel's research (Next.js 16 API eval): skills alone scored 53% — identical to the no-docs baseline (+0pp; the agent skipped invoking the skill in 56% of cases). Skills with explicit prompting reached 79%. An `AGENTS.md` in the project root reached 100%, because its content sits in the system prompt on every turn — no decision point, no ordering issues. Caveats from the article: docs were compressed 40KB -> 8KB to control context cost, results were sensitive to instruction wording, and skills are still recommended for vertical, user-triggered workflows.

## 1.2. The Skill Folder Structure
A valid skill must follow these rules:
- **Folder name**: `kebab-case` only (e.g., `generate-tests`). No spaces or capitals.
- **Required file**: Exactly `SKILL.md` (case-sensitive) containing YAML frontmatter and markdown instructions.
- **No README.md**: Do not put a README.md inside the skill folder itself.
- **Progressive Disclosure**: Keep `SKILL.md` focused and under 5000 words. Place detailed documentation in a `references/` directory and link to it.

## 1.3. YAML Frontmatter Requirements
The YAML frontmatter tells Claude when to use the skill:
- `name`: kebab-case, no spaces or capitals.
- `description`: Under 1024 characters. Must include BOTH what the skill does AND when to use it (trigger conditions/phrases).
- Forbidden: XML angle brackets (`<`, `>`) and the words 'claude' or 'anthropic' in the name.

## 1.4. Effective Instructions
- Use clear, actionable steps.
- Include Error Handling (e.g., 'If validation fails, common issues include...').
- Provide examples of good and bad outputs.

---

# Part 2: Google's Testing on the Toilet Principles

This section contains an exhaustive summary of Google's unit testing principles, including those not yet implemented as explicit rules in the repository.

## 2.1. High-Priority Testing Principles

### Increase Test Fidelity By Avoiding Mocks
Fidelity = how closely test behavior resembles production behavior. Preference order: use the real implementation; use a fake if the real one is too slow, non-deterministic, or hard to instantiate; use a mock only if neither is possible. Mocks remain especially useful for hard-to-trigger paths (e.g. timeouts). Keep tests 'small' (single process) while raising fidelity. Fakes should be created and maintained by the owner of the real implementation.

### Don't Mock Types You Don't Own
Mocking third-party types makes maintenance harder: library upgrades break stale mock assumptions and can hide real bugs. Preference order per the post: (1) use the real implementation, (2) use a fake ideally provided by the library owner, (3) only as a last resort wrap the type in your own class and mock the wrapper — and test the wrapper itself against the real implementation. (Credited to Freeman & Pryce, GOOS.)

### Only Verify State-Changing Method Calls
Usually avoid verifying that non-state-changing methods (queries/getters) were called — it is redundant, brittle, and gives false confidence. Verify state-changing calls (SendEmail, SaveRecord) instead, and use queries for stubbing. Exception: verifying a query call is useful when there is no other observable output (e.g. asserting an RPC happens exactly once to test caching). Better still: use a real or fake object and assert the resulting state.

### Change-Detector Tests Considered Harmful
A change-detector test is a transformation of the same information in the code under test — it breaks on any production change without verifying correct behavior (a 'checksum' of the source). Such tests provide negative value: rewrite or delete them. Test behaviors, not implementation.

### Know Your Test Doubles
Stub: no logic, only returns what you tell it. Mock: has expectations about how it is called; used for interaction testing when there is no visible state or return value. Fake: a lightweight working implementation of the API unsuitable for production (e.g. in-memory database), built without a mocking framework — usually created and maintained by the real implementation's owner. (Terminology from Meszaros, xUnit Test Patterns.)

### Fake Your Way to Better Tests
Use fakes when the real implementation is too slow or non-deterministic. Fakes should be created and maintained by the owner of the real implementation, need their own tests (ideally the same contract tests run against both real and fake), and should be applied at the lowest layer possible — if a dependency can't be faked, wrap the untestable part and fake the wrapper. Keep a small number of integration tests against the real implementation.

### Don't Overuse Mocks
Over-mocked tests are harder to understand, leak implementation details into the test, and give less assurance (they only prove the code works if the mocks behave exactly like the real implementations — which drifts). Heuristics: mocking more than 1-2 collaborators, a mock stubbing more than 1-2 methods, or needing to step through production code to understand the test. Alternatives: real objects, fakes, hermetic local servers.

### Testing State vs. Testing Interactions
In most cases test state, not interactions: a passing interaction test proves a method was called, not that the result is correct (that Sort() was invoked says nothing about whether sorting works). Interaction testing is legitimate when correctness depends on HOW the result is produced: call count or order matters (exactly one email sent, bounded reads, deadlock-avoiding order) or MVC/MVP-style UI wiring.

## 2.2. Medium and Low Priority Principles

### Separation of Concerns? That's a Wrap!
Wrap external/third-party APIs behind your own types so API-call details stay out of domain logic — for maintainability, insulation from API changes, easier swapping, and readability. Caveat (YAGNI): don't wrap when the effort is huge or the API is simple and stable (e.g. List).

### Tests Too DRY? Make Them DAMP!
Production code should be DRY, but tests should be DAMP (Descriptive And Meaningful Phrases). Duplication in tests is acceptable when it improves readability and makes each test understandable at a glance. DAMP complements DRY rather than replacing it — helpers are still fine when they don't hurt clarity.

### Exercise Service Call Contracts in Tests
If code under test relies on a service's contract, prefer exercising the service call over mocking it out: use a fast, lightweight fake maintained by the service owners (don't hand-roll one you can't keep in sync), or a hermetic server started by the test on the same machine (slower). Mocks may be the only option when neither exists — then compensate with end-to-end tests or manual QA.

---

# Part 3: Active Skill Rules Repository

# General Rules

## cleanly-create-test-data.md

---
title: Cleanly Create Test Data
impact: HIGH
impactDescription: improves test readability and maintainability through clean data setup
tags: tests, test-data, helpers, builders, readability
---

## Cleanly Create Test Data

Use helper functions and builder patterns to create test data cleanly. Avoid cluttering tests with irrelevant details.

### Use Helper Functions

Helper functions hide irrelevant details and make tests easier to read.

**Incorrect:**

```csharp
[Fact]
public void CalculateTotal_MultipleItems_HappyPath()
{
    ShoppingCart shoppingCart = new ShoppingCart(new DefaultRoundingStrategy(),
        "unused", Mode.Normal, false, false, TimeZoneInfo.Utc, null);
    int totalPrice = shoppingCart.CalculateTotal(
        NewItem1(),
        NewItem2(),
        NewItem3());
    totalPrice.Should().Be(25); // Where did this number come from?
}
```

**Correct:**

```csharp
[Fact]
public void CalculateTotal_MultipleItems_HappyPath()
{
    ShoppingCart shoppingCart = NewShoppingCart();

    int actualTotal = shoppingCart.CalculateTotal(
        NewItemWithPrice(10),
        NewItemWithPrice(10),
        NewItemWithPrice(5));

    int expectedTotal = 25;
    actualTotal.Should().Be(expectedTotal);
}
```

### Use the Test Data Builder Pattern

When helper methods grow with many parameters, use the builder pattern.

**Incorrect:**

```csharp
// Helper methods become unwieldy with many parameters
Company small = NewCompany(2, 2, null, CompanyType.Public);
Company privatelyOwned = NewCompany(null, null, null, CompanyType.Private);
Company bankrupt = NewCompany(null, null, PastDate, CompanyType.Public);
```

**Correct:**

```csharp
Company small = NewCompany().WithEmployeesCount(2).WithBoardMembersCount(2).Build();
Company privatelyOwned = NewCompany().WithType(CompanyType.Private).Build();
Company bankrupt = NewCompany().WithBankruptcyDate(PastDate).Build();
Company arbitraryCompany = NewCompany().Build();

// Helper returns builder with required defaults
private static CompanyBuilder NewCompany()
{
    return new CompanyBuilder().WithType(CompanyType.Public);
}
```

### Never Rely on Default Values from Helpers

If a test depends on a value, explicitly set it even if it matches the helper's default.

**Incorrect:**

```csharp
private static CompanyBuilder NewCompany()
{
    return new CompanyBuilder().WithType(CompanyType.Public);
}

[Fact]
public void Test_PublicCompany()
{
    // Relies on helper's default - fragile!
    Company company = NewCompany().Build();
    // ...
}
```

**Correct:**

```csharp
[Fact]
public void Test_PublicCompany()
{
    // Explicitly set the value this test depends on
    Company company = NewCompany()
        .WithType(CompanyType.Public)  // Explicit even if matches default
        .WithBoardMembersCount(0)
        .Build();
    // ...
}
```

### Helper Function Guidelines

1. **Name helpers descriptively** - `CreateProductWithCategory("Office")` not `CreateProduct()`
2. **Only expose relevant parameters** - hide irrelevant details
3. **Keep helpers simple** - no business logic
4. **Consider builders for complex objects** - when many field combinations are needed


---

## code-context-analysis.md

---
title: Code Context Analysis
impact: HIGH
impactDescription: ensures correct test data by understanding the full dependency graph
tags: tests, context, dependencies, dto, entity, analysis
---

## Code Context Analysis

Before generating tests, read all types referenced by the target code. Tests that use wrong constructors, miss required fields, or create invalid objects will fail at compile time or produce meaningless results.

### What to Read Before Writing Tests

After reading the target class, identify and read:

1. **Direct parameter types**: Every class used as a method parameter
2. **Return types**: Every class returned by the method under test
3. **Field types injected via constructor**: Dependencies that need substituting
4. **Domain entities / DTOs**: Classes created or transformed in the method body
5. **Enums**: Any enum used in conditionals, switch statements/expressions, or as parameters
6. **Custom exceptions**: Exception classes thrown by the method
7. **Validators / Constraints**: Custom attribute classes if validation is tested

### Why This Matters

**Without reading dependencies:**
```csharp
// Compiles but FAILS - wrong constructor args
var request = new OrderRequest("product-1", 5);
// Actual constructor: OrderRequest(string productId, int quantity, string customerId)
```

**With reading dependencies:**
```csharp
// Correct - matches the actual constructor
var request = new OrderRequest("product-1", 5, "customer-123");
```

### How to Read Dependencies Efficiently

1. Read the target class's using directives and namespace to identify referenced types
2. Use Glob to find the source files: `**/OrderRequest.cs`
3. Read each dependency to understand:
   - Constructor parameters (types and order)
   - Required fields vs optional fields
   - Builder patterns (if present — use the builder)
   - Factory methods (if present — prefer over constructors)
   - Enum values available

### Pay Special Attention To

- **Object construction patterns**: records (positional constructors), `required` members, `init`-only setters, primary constructors, and static factory methods change how objects are constructed
- **Validation attributes**: `[Required]`, `[StringLength]`, `[Range]` on properties indicate constraints that tests should satisfy (or intentionally violate for negative tests)
- **Inheritance**: If a class extends another, read the parent class too
- **Generics**: Understand the type parameters to use correct types in tests

### Checklist

Before writing any test method:
- [ ] Read all parameter types used by the target method
- [ ] Read all return types
- [ ] Read domain entities created or modified in the method body
- [ ] Read enum classes used in conditionals
- [ ] Identified constructors, builders, or factory methods for test data creation


---

## existing-test-awareness.md

---
title: Existing Test Awareness
impact: HIGH
impactDescription: prevents duplicate tests and ensures consistency with project conventions
tags: tests, awareness, duplicates, conventions, style
---

## Existing Test Awareness

Before generating tests, check what already exists. Match the project's testing conventions and avoid duplicating coverage.

### Before Generating: Check for Existing Tests

1. **Look for an existing test class** for the target:
   - Search for `{ClassName}Tests` in the test project
   - If found, read it fully before generating anything

2. **If an existing test class is found:**
   - Do NOT create a new test class — add missing test methods to the existing one
   - Preserve existing test structure, using directives, and helper methods
   - Follow the same patterns (naming, assertion style, setup approach) already used
   - Only add tests for behaviors not yet covered

3. **If no existing test class is found:**
   - Scan 2-3 neighboring test classes in the same namespace to learn project conventions
   - Match the style: using directive order, assertion library, naming pattern, comment style

### What to Match from Existing Tests

- **Assertion library**: Don't switch styles (e.g. AwesomeAssertions/FluentAssertions vs Shouldly vs plain xUnit `Assert`) — keep what the project already uses
- **Test data patterns**: If the project has a `TestDataFactory` or builders, use them
- **Base test classes**: If tests extend a `TestBase` or `IntegrationTestBase`, follow that pattern
- **Using directive style**: Match how the project imports assertion/substitute namespaces (e.g., `using static`, global usings)
- **Comment style**: If existing tests use `// given / when / then` vs `// arrange / act / assert`, match it

### What NOT to Do

**Incorrect:**

```csharp
// Creating a new test class when one already exists
// File: UserServiceTests.cs (NEW - duplicate!)
public class UserServiceTests
{
    // 10 test methods, 5 of which already exist in the old file
}
```

**Correct:**

```csharp
// Adding only missing tests to the existing file
// File: UserServiceTests.cs (EXISTING - appended to)
public class UserServiceTests
{
    // ... existing tests preserved as-is ...

    // New tests added below existing ones
    [Fact]
    public void UpdateUser_InvalidEmail_ThrowsValidationException()
    {
        // ...
    }
}
```

### Decision Checklist

Before writing any test code, verify:
- [ ] Searched for existing test class for the target
- [ ] Read existing tests to understand what's already covered
- [ ] Identified project test conventions from neighboring test files
- [ ] Confirmed which behaviors still need test coverage


---

## general-principles.md

---
title: General Test Principles
impact: HIGH
impactDescription: ensures tests are maintainable, reliable, and focused on behavior
tags: tests, principles, patterns, best-practices
---

## General Test Principles

Follow these core principles for writing effective, maintainable tests.

### 1. Use Given-When-Then / Arrange-Act-Assert Pattern

Structure every test with clear sections for setup, action, and verification. In C#, use `// Arrange` / `// Act` / `// Assert` comments — the .NET convention for the same structure Given-When-Then provides.

**Incorrect:**

```csharp
[Fact]
public void CalculateTotal()
{
    var result = _service.CalculateTotal(new List<Product> { product1, product2 });
    Assert.Equal(150.0m, result);
    _repository.Received().FindAll();
}
```

**Correct:**

```csharp
[Fact]
public void CalculateTotal_ValidProducts_ReturnsSum()
{
    // Arrange
    var product1 = new Product("A", 50.0m);
    var product2 = new Product("B", 100.0m);
    _repository.FindAll().Returns(new List<Product> { product1, product2 });

    // Act
    decimal actualTotal = _service.CalculateTotal();

    // Assert
    decimal expectedTotal = 150.0m;
    actualTotal.Should().Be(expectedTotal);
}
```

### 2. Use "actual" and "expected" Prefixes

Clearly distinguish between expected and actual values for better readability.

**Incorrect:**

```csharp
var result = _service.GetUser(id);
result.Name.Should().Be(name);
```

**Correct:**

```csharp
var actualUser = _service.GetUser(id);
var expectedName = "John Doe";
actualUser.Name.Should().Be(expectedName);
```

### 3. Focus on Behavior, Not Implementation

Test externally visible effects, not internal implementation details.

**Incorrect:**

```csharp
// Testing implementation details
[Fact]
public void CalculateTotal_UsesParallelQuery()
{
    // verifying internal PLINQ usage
}
```

**Correct:**

```csharp
// Testing behavior
[Fact]
public void CalculateTotal_LargeDataset_ReturnsCorrectSum()
{
    // verifying the result, not how it's computed
}
```

### 4. Keep Tests Deterministic and Simple

Tests must produce the same result every time. Avoid business logic in tests.

**Incorrect:**

```csharp
[Fact]
public void CreateOrder_SetsTimestamp()
{
    var order = _service.CreateOrder();
    order.Timestamp.Should().BeCloseTo(DateTimeOffset.UtcNow, TimeSpan.FromSeconds(1));
}
```

**Correct:**

```csharp
[Fact]
public void CreateOrder_SetsTimestamp()
{
    // Arrange - inject a fixed TimeProvider (or an IClock abstraction)
    var timeProvider = Substitute.For<TimeProvider>();
    timeProvider.GetUtcNow().Returns(DateTimeOffset.Parse("2024-01-01T00:00:00Z"));
    var service = new OrderService(timeProvider);

    // Act
    var actualOrder = service.CreateOrder();

    // Assert
    actualOrder.Timestamp.Should().Be(DateTimeOffset.Parse("2024-01-01T00:00:00Z"));
}
```

### 5. Verify Only Relevant Outputs and Interactions

Don't overuse substitutes. Never substitute the system under test or simple value objects.

**Incorrect:**

```csharp
// Over-mocking
[Fact]
public void ProcessOrder()
{
    var productSubstitute = Substitute.For<IProduct>();
    productSubstitute.Price.Returns(100.0m);
    productSubstitute.Name.Returns("Test");
    // ...
}
```

**Correct:**

```csharp
// Use real objects for simple value objects
[Fact]
public void ProcessOrder_ValidProduct_CalculatesTotal()
{
    // Arrange
    var product = new Product("Test", 100.0m); // real object

    // Act
    var actualResult = _service.ProcessOrder(product);

    // Assert
    actualResult.Total.Should().Be(100.0m);
}
```

### 6. Use Helpers and Builders to Remove Duplication

Extract common setup logic into helper methods or builders.

**Incorrect:**

```csharp
[Fact]
public void Test1()
{
    var user = new User
    {
        Name = "John",
        Email = "john@test.com",
        Role = Role.Admin
    };
    // ...
}

[Fact]
public void Test2()
{
    var user = new User
    {
        Name = "Jane",
        Email = "jane@test.com",
        Role = Role.User
    };
    // ...
}
```

**Correct:**

```csharp
[Fact]
public void Test1()
{
    var user = CreateUser("John", "john@test.com", Role.Admin);
    // ...
}

[Fact]
public void Test2()
{
    var user = CreateUser("Jane", "jane@test.com", Role.User);
    // ...
}

private static User CreateUser(string name, string email, Role role)
{
    return new User
    {
        Name = name,
        Email = email,
        Role = role
    };
}
```


---

## keep-cause-effect-clear.md

---
title: Keep Cause and Effect Clear
impact: HIGH
impactDescription: ensures tests are self-contained and easy to understand
tags: tests, readability, cause-effect, self-contained
---

## Keep Cause and Effect Clear

Write tests where the effects immediately follow the causes. Avoid relying on distant setup code.

### Problem: Hidden Setup

When setup is far from the test, it's impossible to understand the test without scrolling. In xUnit the constructor runs before every test (a fresh test-class instance is created per test), so test-specific data in the constructor is just as hidden as it would be in any setup method.

**Incorrect:**

```csharp
private readonly Counter _counter = new Counter();

public CounterTests()
{
    _counter.Increment("key1", 8);
    _counter.Increment("key2", 100);
    _counter.Increment("key1", 0);
    _counter.Increment("key1", 1);
}

// ... 200 lines later ...

[Fact]
public void TestIncrement_ExistingKey()
{
    // Where does 9 come from? Have to scroll up to find out!
    _counter.Get("key1").Should().Be(9);
}
```

**Correct:**

```csharp
private readonly Counter _counter = new Counter();

[Fact]
public void Increment_NewKey_SetsValue()
{
    // Cause and effect are together
    _counter.Increment("key2", 100);

    _counter.Get("key2").Should().Be(100);
}

[Fact]
public void Increment_ExistingKey_AddsToValue()
{
    // Clear cause-effect relationship
    _counter.Increment("key1", 8);
    _counter.Increment("key1", 1);

    _counter.Get("key1").Should().Be(9);
}
```

### Guidelines

1. **Put setup in the test** - if it's relevant to understanding the test
2. **Use the constructor only for** - infrastructure setup (substitutes, SUT construction), not test-specific data
3. **Avoid shared mutable state** - each test should set up its own data
4. **Keep tests self-contained** - reader shouldn't need to look elsewhere

### When Constructor Setup Is Appropriate

The xUnit constructor is the per-test setup (the equivalent of other frameworks' `beforeEach`). Use it for infrastructure, not test data:

```csharp
private readonly WireMockServer _mockServer;
private readonly UserService _service;

public UserServiceTests()
{
    // OK: Infrastructure setup
    _mockServer = WireMockServer.Start();

    // OK: Creating SUT
    _service = new UserService(_mockServer.Url!);
}

[Fact]
public void GetUser_ExistingUser_ReturnsUser()
{
    // Test-specific data belongs in the test
    _mockServer.Given(Request.Create().WithPath("/users/123"))
        .RespondWith(Response.Create().WithBody("{\"name\":\"John\"}"));

    User actualUser = _service.GetUser("123");

    actualUser.Name.Should().Be("John");
}
```

### Benefits

- Tests are **self-documenting** - you understand the test by reading it
- Tests are **independent** - changing one test doesn't break others
- Failures are **easier to debug** - all relevant context is visible


---

## keep-tests-focused.md

---
title: Keep Tests Focused
impact: HIGH
impactDescription: ensures each test verifies one specific scenario for clear failure messages
tags: tests, focused, single-scenario, single-assertion
---

## Keep Tests Focused

Each test should exercise one specific scenario. Multiple scenarios in one test make failures hard to diagnose.

### Problem: Multiple Scenarios in One Test

**Incorrect:**

```csharp
[Fact]
public void WithdrawFromAccount()
{
    Transaction transaction = _account.Deposit(Usd(5));

    // Scenario 1: withdraw within balance
    _account.Withdraw(Usd(5)).Should().Be(IsOk());

    // Scenario 2: withdraw over balance
    _account.Withdraw(Usd(1)).Should().Be(IsRejected());

    // Scenario 3: withdraw with overdraft
    _account.SetOverdraftLimit(Usd(1));
    _account.Withdraw(Usd(1)).Should().Be(IsOk());
}
// This tests three scenarios, not one!
```

**Correct:**

```csharp
[Fact]
public void Withdraw_WithinBalance_Succeeds()
{
    DepositAndSettle(Usd(5));

    _account.Withdraw(Usd(5)).Should().Be(IsOk());
}

[Fact]
public void Withdraw_OverBalance_IsRejected()
{
    DepositAndSettle(Usd(5));

    _account.Withdraw(Usd(6)).Should().Be(IsRejected());
}

[Fact]
public void Withdraw_WithinOverdraftLimit_Succeeds()
{
    DepositAndSettle(Usd(5));
    _account.SetOverdraftLimit(Usd(1));

    _account.Withdraw(Usd(6)).Should().Be(IsOk());
}
```

### Benefits of Focused Tests

1. **Clear failure messages** - you know exactly what broke
2. **Descriptive names** - each test name describes one scenario
3. **Easy to maintain** - changing one scenario doesn't affect others
4. **Better coverage visibility** - see which scenarios are tested

### When Multiple Assertions Are OK

Multiple assertions are fine when verifying **one behavior** with multiple properties:

```csharp
[Fact]
public void CreateUser_ValidInput_ReturnsCompleteUser()
{
    User actualUser = _userService.Create("john@test.com", "John");

    // All assertions verify the same behavior: user creation
    actualUser.Id.Should().NotBeNull();
    actualUser.Email.Should().Be("john@test.com");
    actualUser.Name.Should().Be("John");
    actualUser.CreatedAt.Should().NotBeNull();
}
```

### Signs Your Test Is Not Focused

- Test name uses "And" (e.g., `TestDepositAndWithdraw`)
- Multiple "When" or "Act" sections
- State changes between assertions
- Hard to name the test concisely
- Test is longer than 10-15 lines

### Split Unfocused Tests

Ask: "If this test fails, will I know exactly which scenario broke?"

If not, split it into multiple tests.


---

## naming-conventions.md

---
title: Test Naming Conventions
impact: HIGH
impactDescription: ensures consistent, readable test names that describe behavior
tags: tests, naming, conventions, readability
---

## Test Naming Conventions

Use consistent naming patterns that clearly describe the test scenario and expected outcome.

### Test Class Naming

Use the target language's idioms:
- `[TestedClass]Tests` (C#)
- `test_[module_name].py` (Python)
- `[name].test.js` or `[name].spec.ts` (JavaScript/TypeScript)

### Test Method Naming

Format: `{testedMethod}_{givenState}_{expectedOutcome}`

In C# this renders in PascalCase (`Method_State_Outcome`); in TypeScript/JavaScript it stays camelCase.

**Incorrect:**

```csharp
// Too vague
[Fact]
public void TestCalculate() { ... }

// No outcome described
[Fact]
public void CalculateTotal_ValidProducts() { ... }

// Implementation details instead of behavior
[Fact]
public void CalculateTotal_UsesLinq_ReturnsSum() { ... }
```

**Correct:**

```csharp
// Clear state and outcome
[Fact]
public void CalculateTotal_ValidProducts_ReturnsSum() { ... }

[Fact]
public void CalculateTotal_EmptyList_ThrowsArgumentException() { ... }

[Fact]
public void GetUser_Unauthorized_Returns401() { ... }

[Fact]
public void GetUser_Forbidden_Returns403() { ... }

[Fact]
public void SaveOrder_ValidOrder_PersistsToDatabase() { ... }

[Fact]
public void DeleteUser_NonExistentId_ThrowsNotFoundException() { ... }
```

### Naming Guidelines

1. **Be specific about the state/condition** - "ValidProducts" not "GoodInput"
2. **Be specific about the outcome** - "Returns401" not "Fails"
3. **Use domain language** - "Unauthorized" not "NoToken"
4. **Avoid technical jargon** - describe behavior, not implementation


---

## no-logic-in-tests.md

---
title: Don't Put Logic in Tests
impact: HIGH
impactDescription: prevents bugs in tests and makes expected values obvious
tags: tests, simplicity, kiss, no-logic, readability
---

## Don't Put Logic in Tests

Tests should be straightforward with no conditional logic, loops, or string concatenation. Keep expected values explicit and literal.

### KISS > DRY in Tests

Simplicity is more important than avoiding duplication in tests.

### Problem: Logic Hides Bugs

**Incorrect:**

```csharp
[Fact]
public void GetPhotosPageUrl()
{
    string baseUrl = "http://photos.google.com/";
    UrlBuilder urlBuilder = new UrlBuilder(baseUrl);

    string photosPageUrl = urlBuilder.GetPhotosPageUrl();

    // Bug hidden by concatenation: results in "//u/0/photos"
    photosPageUrl.Should().Be(baseUrl + "/u/0/photos");
}
```

**Correct:**

```csharp
[Fact]
public void GetPhotosPageUrl_HappyPath()
{
    UrlBuilder urlBuilder = new UrlBuilder("http://photos.google.com/");

    string actualUrl = urlBuilder.GetPhotosPageUrl();

    // Explicit literal - bug is obvious: "http://photos.google.com//u/0/photos"
    actualUrl.Should().Be("http://photos.google.com/u/0/photos");
}
```

### Avoid These Patterns in Tests

**Incorrect:**

```csharp
// Loops in tests
for (int i = 0; i < users.Count; i++)
{
    users[i].IsActive.Should().BeTrue();
}

// Conditionals in tests
if (response.IsSuccessful)
{
    response.Body.Should().NotBeNull();
}

// String concatenation in assertions
result.Should().Be("Hello, " + userName + "!");

// Calculations in assertions
total.Should().Be(price * quantity + tax);
```

**Correct:**

```csharp
// Explicit assertions
users.Should().OnlyContain(u => u.IsActive);

// No conditionals - test specific scenarios
response.IsSuccessful.Should().BeTrue();
response.Body.Should().NotBeNull();

// Literal expected values
result.Should().Be("Hello, John!");

// Pre-calculated expected values
int expectedTotal = 115; // 100 * 1 + 15 tax, calculated outside test
total.Should().Be(expectedTotal);
```

### When Logic is Necessary

If tests need complex logic, move it to helper functions with their own tests:

```csharp
// Helper with its own test coverage
public static class TestDataGenerator
{
    public static string GenerateExpectedGreeting(User user, DateOnly date)
    {
        // Complex logic here
    }
}

// TestDataGeneratorTests verifies this helper works correctly
```

### Key Principles

1. **Use literal values** - not computed values
2. **Avoid operators** - no `+`, `*`, string concatenation in assertions
3. **No control flow** - no `if`, `for`, `while` in test bodies
4. **KISS over DRY** - repetition is OK if it makes tests clearer


---

## prefer-public-apis.md

---
title: Prefer Testing Public APIs Over Private Methods
impact: HIGH
impactDescription: creates resilient tests that survive refactoring
tags: tests, public-api, private-methods, refactoring, resilience
---

## Prefer Testing Public APIs Over Private Methods

Test the public interface of your code. Private methods and implementation-detail classes should be tested indirectly through public APIs.

### Problem: Testing Implementation Details

**Incorrect:**

```csharp
// Testing private helper class directly
public class UserInfoValidatorTests
{
    [Fact]
    public void Validate_FutureDateOfBirth_ThrowsException()
    {
        UserInfoValidator validator = new UserInfoValidator();

        validator.Invoking(v => v.Validate(InfoWithFutureDob()))
            .Should().Throw<ValidationException>();
    }
}

// This test is fragile - if we inline or rename the validator, test breaks
```

**Correct:**

```csharp
// Test through the public API
public class UserInfoServiceTests
{
    [Fact]
    public void Save_FutureDateOfBirth_ThrowsValidationException()
    {
        UserInfoService service = new UserInfoService();
        UserInfo info = CreateUserInfo().WithDateOfBirth(FutureDate).Build();

        service.Invoking(s => s.Save(info))
            .Should().Throw<ValidationException>()
            .WithMessage("Invalid date of birth");
    }

    [Fact]
    public void Save_ValidInfo_PersistsToDatabase()
    {
        UserInfoService service = new UserInfoService();
        UserInfo info = CreateUserInfo().WithDateOfBirth(PastDate).Build();

        service.Save(info);

        _database.FindById(info.Id).Should().NotBeNull();
    }
}
```

### When to Test Private/Internal Classes

Test implementation classes separately only when:
1. **Reused across multiple public APIs** - becomes part of the public contract
2. **Complex enough to warrant isolation** - but consider if it should be extracted
3. **Third-party integration** - adapters that wrap external libraries

### Refactoring Freedom

Testing public APIs allows refactoring without changing tests:

```csharp
// Original implementation
public class UserInfoService
{
    private readonly UserInfoValidator _validator = new UserInfoValidator();

    public void Save(UserInfo info)
    {
        _validator.Validate(info);
        WriteToDatabase(info);
    }
}

// Refactored - validator inlined
public class UserInfoService
{
    public void Save(UserInfo info)
    {
        if (info.DateOfBirth.IsInFuture())
        {
            throw new ValidationException("Invalid date of birth");
        }
        WriteToDatabase(info);
    }
}

// Tests don't change because they test the public API!
```

### Guidelines

1. **Test behavior, not implementation** - focus on what, not how
2. **Use public methods as entry points** - even for testing edge cases
3. **Private methods are implementation** - should be covered by public method tests
4. **Consider visibility carefully** - if something needs direct testing, maybe it should be public


---

## technology-stack-detection.md

---
title: Technology Stack Detection
impact: MEDIUM
impactDescription: ensures tests use correct frameworks and conventions for the project
tags: tests, technology, detection, frameworks, conventions
---

## Technology Stack Detection

When writing tests, first detect the programming language and technology stack from the project.

### Build/Package File Detection

| File | Language/Framework |
|------|-------------------|
| `*.csproj` / `*.sln` | C# (.NET) |
| `package.json` | JavaScript/TypeScript (npm/yarn) — then detect the test framework: `vitest.config.*` or `vitest` in devDependencies → Vitest; `jest.config.*` or a `"jest"` key in package.json → Jest. Never mix the two APIs. |
| `pyproject.toml` / `setup.py` / `requirements.txt` | Python |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `Gemfile` | Ruby |
| `mix.exs` | Elixir |
| `build.sbt` | Scala |
| `composer.json` | PHP |
| `Package.swift` | Swift |

### Test File Locations by Language

| Language | Test Location |
|----------|---------------|
| C# (.NET) | `<Project>.Tests/<ClassName>Tests.cs` |
| Python | `tests/test_<module_name>.py` or `<module>_test.py` |
| JavaScript/TypeScript | `__tests__/<name>.test.js` or `<name>.spec.ts` |
| Go | `<name>_test.go` (same directory as source) |
| Rust | `src/<name>.rs` with `#[cfg(test)]` module or `tests/` directory |
| Ruby | `spec/<name>_spec.rb` or `test/<name>_test.rb` |
| PHP | `tests/<ClassName>Test.php` |
| Elixir | `test/<name>_test.exs` |
| Scala | `src/test/scala/<package>/<ClassName>Spec.scala` |
| Swift | `Tests/<Name>Tests/<Name>Tests.swift` |

### Language-Specific Conventions

**Apply automatically based on detected stack:**

1. Use the idiomatic test framework for the detected language
2. Follow the language's naming conventions for test files and methods
3. Place test files in the standard location for that ecosystem
4. Use the language's preferred assertion style

**Incorrect:**

```csharp
// Using Python-style naming in C#
public void test_calculate_total() { ... }

// Placing C# tests in wrong location
// src/CalculatorTests.cs inside the production project (wrong)
```

**Correct:**

```csharp
// C# conventions
// Location: tests/Calculator.Tests/CalculatorTests.cs
public void CalculateTotal_ValidInput_ReturnsSum() { ... }
```

```python
# Python conventions
# Location: tests/test_calculator.py
def test_calculate_total_valid_input_returns_sum():
    ...
```


---

## test-behaviors-not-methods.md

---
title: Test Behaviors, Not Methods
impact: HIGH
impactDescription: creates resilient tests that survive refactoring
tags: tests, behaviors, resilient, maintainable
---

## Test Behaviors, Not Methods

Structure tests around behaviors (what the system does), not around methods (how it's implemented).

### Problem: Testing a Method

**Incorrect:**

```csharp
[Fact]
public void TestResetPassword()
{
    User user = new User { Password = "lost password" };

    _userService.ResetPassword(user);

    // Testing multiple behaviors in one test
    user.Password.Should().BeEmpty();
    user.Mailbox.Messages[0].Title.Should().Be("Password reset");
    user.Mailbox.Messages[0].Body
        .Should().StartWith("You have requested password reset");
    _counter.Get("reset password").Should().Be(1);
}
```

**Correct:**

```csharp
[Fact]
public void ResetPassword_ClearsExistingPassword()
{
    User user = new User { Password = "1234" };

    _userService.ResetPassword(user);

    user.Password.Should().BeEmpty();
}

[Fact]
public void ResetPassword_SendsNotificationEmail()
{
    User user = new User { Password = "1234" };

    _userService.ResetPassword(user);

    user.Mailbox.Messages[0].Title.Should().Be("Password reset");
    user.Mailbox.Messages[0].Body
        .Should().StartWith("You have requested password reset");
}

[Fact]
public void ResetPassword_IncrementsResetCounter()
{
    User user = new User { Password = "1234" };

    _userService.ResetPassword(user);

    _counter.Get("reset password").Should().Be(1);
}
```

### Benefits

1. **Clear test names** - each test describes one behavior
2. **Focused failures** - when a test fails, you know which behavior broke
3. **Easier refactoring** - changes to one behavior don't affect other tests
4. **Better documentation** - tests describe what the system does

### Identifying Behaviors

Ask: "What are the observable effects of this action?"

For `ResetPassword()`:
- User's password becomes empty
- User receives an email
- Reset counter is incremented

Each of these is a separate behavior that should have its own test.

### One Behavior Can Have Multiple Assertions

Testing the email notification behavior:

```csharp
[Fact]
public void ResetPassword_SendsCorrectNotificationEmail()
{
    User user = new User { Password = "1234", Email = "john@test.com" };

    _userService.ResetPassword(user);

    // Multiple assertions about the same behavior (the email)
    Message actualEmail = user.Mailbox.Messages[0];
    actualEmail.To.Should().Be("john@test.com");
    actualEmail.Title.Should().Be("Password reset");
    actualEmail.Body.Should().StartWith("You have requested");
}
```

### Naming Pattern

Name tests after the behavior, not the method:
- `ResetPassword_ClearsPassword` - describes behavior
- `TestResetPassword` - describes method (bad)


---

## test-case-generation-strategy.md

---
title: Test Case Generation Strategy
impact: HIGH
impactDescription: ensures comprehensive coverage without redundant tests
tags: tests, test-cases, strategy, coverage, branches
---

## Test Case Generation Strategy

Apply strict INCLUDE/EXCLUDE criteria to generate meaningful test cases that cover all code branches without redundancy.

### INCLUDE:
- Each distinct code branch and outcome (success paths, error handling)
- Each unique return value or exception the method can produce
- For HTTP methods: separate cases for status 400, 401, 403 (never merge these)
- Use concrete status codes only
- **Validation constraints**: Generate NEGATIVE test cases for each validation attribute (invalid input that should fail validation)
- **Custom validators**: Generate test cases that trigger validation failure

### EXCLUDE:
- Duplicate scenarios with same observable result
- Collection size variations (1, 2, 3 elements) unless code has EXPLICIT size-dependent logic
- Speculative cases (exotic Unicode, massive payload) unless code explicitly handles them
- Null arguments unless the parameter is declared with a nullable annotation (`T?`)
- Multiple tests for same exception type

**Incorrect:**

```csharp
// Merging different HTTP status codes
[Fact]
public void GetUser_InvalidRequest_Returns4xx() { ... }

// Testing collection sizes without explicit logic
[Fact]
public void ProcessItems_OneItem_Success() { ... }
[Fact]
public void ProcessItems_TwoItems_Success() { ... }
[Fact]
public void ProcessItems_ThreeItems_Success() { ... }

// Testing null without a nullable parameter declaration
[Fact]
public void Calculate_NullInput_ThrowsException() { ... }
```

**Correct:**

```csharp
// Separate tests for each HTTP status
[Fact]
public void GetUser_InvalidInput_Returns400() { ... }
[Fact]
public void GetUser_Unauthenticated_Returns401() { ... }
[Fact]
public void GetUser_Forbidden_Returns403() { ... }

// Single test for collection processing (no size-dependent logic)
[Fact]
public void ProcessItems_ValidList_ReturnsProcessedResult() { ... }

// Only test null if the parameter is nullable
[Fact]
public void Calculate_NullableInput_ReturnsDefault() { ... } // only if parameter is T?
```

### CRITICAL: Private/Protected Methods

When a method calls private/protected methods, cover ALL their execution paths indirectly via different inputs to the public method.

### Decision Strategy

Before adding each test case, ask:
1. Does it trigger a DIFFERENT code branch? If no -> skip
2. Does it produce a DIFFERENT observable outcome? If no -> skip
3. Does the code EXPLICITLY check this condition? If no -> skip

**FORBIDDEN:** Using "2xx", "4xx", "5xx" instead of concrete status codes (200, 400, 401, 403, 500).


---

## verify-relevant-arguments-only.md

---
title: Only Verify Relevant Method Arguments
impact: MEDIUM
impactDescription: reduces test fragility and focuses verification on tested behavior
tags: tests, verification, mocks, arguments, focused
---

## Only Verify Relevant Method Arguments

When verifying substitute interactions, only check arguments that are relevant to the specific behavior being tested. Use `Arg.Any<T>()` for irrelevant arguments.

### Problem: Over-Specified Verification

**Incorrect:**

```csharp
[Fact]
public void DisplayGreeting_ShowsSpecialGreetingOnNewYearsDay()
{
    _clock.SetTime(NewYearsDay);
    _user.Name = "Frank Sinatra";

    _userGreeter.DisplayGreeting();

    // Verifying ALL arguments - fragile!
    _userPrompter.Received(1).UpdatePrompt(
        "Hi Frank Sinatra! Happy New Year!",
        TitleBar.Of("2024-01-01"),
        PromptStyle.Normal);
}
// This test breaks if TitleBar format or PromptStyle changes,
// even though it's testing the greeting message
```

**Correct:**

```csharp
[Fact]
public void DisplayGreeting_ShowsSpecialGreetingOnNewYearsDay()
{
    _clock.SetTime(NewYearsDay);
    _user.Name = "Frank Sinatra";

    _userGreeter.DisplayGreeting();

    // Only verify the argument this test cares about
    _userPrompter.Received(1).UpdatePrompt(
        "Hi Frank Sinatra! Happy New Year!", Arg.Any<TitleBar>(), Arg.Any<PromptStyle>());
}

[Fact]
public void DisplayGreeting_UsesTitleBarWithCurrentDate()
{
    _clock.SetTime(NewYearsDay);

    _userGreeter.DisplayGreeting();

    // This test focuses on TitleBar
    _userPrompter.Received(1).UpdatePrompt(
        Arg.Any<string>(), TitleBar.Of("2024-01-01"), Arg.Any<PromptStyle>());
}

[Fact]
public void DisplayGreeting_UsesNormalPromptStyle()
{
    _userGreeter.DisplayGreeting();

    // This test focuses on PromptStyle
    _userPrompter.Received(1).UpdatePrompt(
        Arg.Any<string>(), Arg.Any<TitleBar>(), PromptStyle.Normal);
}
```

### Benefits

1. **Focused tests** - each test verifies one behavior
2. **Resilient tests** - changes to unrelated arguments don't break tests
3. **Clear intent** - obvious what behavior is being tested

### When to Verify All Arguments

Verify all arguments only when they're all relevant to the behavior:

```csharp
[Fact]
public void SendEmail_AllFieldsAreCorrect()
{
    // When testing the complete email composition
    _orderService.SendConfirmation(order);

    _emailService.Received(1).Send(
        "customer@test.com",
        "Order Confirmation #123",
        Arg.Is<string>(body => body.Contains("Thank you for your order")));
}
```

### Combining with Argument Capture

For complex objects, capture with `Arg.Do<T>` and verify only relevant fields:

```csharp
[Fact]
public void CreateOrder_SetsCorrectProductId()
{
    Order? capturedOrder = null;
    _repository.Save(Arg.Do<Order>(o => capturedOrder = o));

    _orderService.CreateOrder(new OrderRequest("product-123", 5));

    // Only verify the field relevant to this test
    capturedOrder!.ProductId.Should().Be("product-123");
}
```


---

## what-makes-good-test.md

---
title: What Makes a Good Test
impact: HIGH
impactDescription: defines core qualities that every test should have
tags: tests, quality, clarity, completeness, conciseness, resilience
---

## What Makes a Good Test

Every good test should have four qualities: Clarity, Completeness, Conciseness, and Resilience.

### 1. Clarity

A test should be easy to read and understand at a glance.

**Signs of clarity:**
- Test name describes the scenario
- Arrange-Act-Assert (Given-When-Then) structure is obvious
- No need to look elsewhere to understand the test

**Incorrect:**

```csharp
[Fact]
public void Test1()
{
    var x = _svc.Process(GetData());
    Assert.True(x.IsValid);
}
```

**Correct:**

```csharp
[Fact]
public void Process_ValidInput_ReturnsValidResult()
{
    // Arrange
    var input = CreateValidInput();

    // Act
    var actualResult = _service.Process(input);

    // Assert
    actualResult.IsValid.Should().BeTrue();
}
```

### 2. Completeness

A test should contain all information needed to understand it without looking elsewhere.

**Incorrect:**

```csharp
// Relies on class-level constants and constructor setup
[Fact]
public void TestCalculation()
{
    _calculator.Calculate().Should().Be(ExpectedValue);
}
```

**Correct:**

```csharp
[Fact]
public void Calculate_MultipleItems_ReturnsSumOfPrices()
{
    // All relevant data is visible in the test
    _calculator.Add(NewItemWithPrice(10));
    _calculator.Add(NewItemWithPrice(20));

    int actualTotal = _calculator.Calculate();

    int expectedTotal = 30;
    actualTotal.Should().Be(expectedTotal);
}
```

### 3. Conciseness

A test should contain only information relevant to the scenario. Hide irrelevant details.

**Incorrect:**

```csharp
[Fact]
public void GetUser_ExistingUser_ReturnsUser()
{
    var user = new User
    {
        Id = "123",
        Name = "John",
        Email = "john@test.com",
        CreatedAt = DateTimeOffset.UtcNow,
        UpdatedAt = DateTimeOffset.UtcNow,
        Role = Role.User,
        IsActive = true
    };
    // ... more irrelevant setup
}
```

**Correct:**

```csharp
[Fact]
public void GetUser_ExistingUser_ReturnsUser()
{
    // Helper hides irrelevant details
    var user = CreateUser("123", "John");
    _repository.FindById("123").Returns(user);

    var actualUser = _service.GetUser("123");

    actualUser.Name.Should().Be("John");
}
```

### 4. Resilience

A test should not break when unrelated code changes. It should only fail when the tested behavior breaks.

**Signs of resilience:**
- Tests behavior, not implementation
- Uses public APIs
- Doesn't over-specify substitute interactions
- Doesn't rely on specific field order or formatting

**Incorrect:**

```csharp
// Brittle: breaks if JSON field order changes
response.Body.Should().Be("{\"name\":\"John\",\"age\":30}");
```

**Correct:**

```csharp
// Resilient: only checks relevant fields
response.Body.Should().Contain("\"name\":\"John\"");
// Or parse the JSON and check the field
JsonDocument.Parse(response.Body).RootElement
    .GetProperty("name").GetString().Should().Be("John");
```

### Summary Checklist

- [ ] **Clarity**: Can I understand this test in 10 seconds?
- [ ] **Completeness**: Is all relevant information in the test?
- [ ] **Conciseness**: Is irrelevant information hidden?
- [ ] **Resilience**: Will this test survive refactoring?


---

# C# / .NET Rules

## controller-test-rules.md

---
title: Controller Test Rules
impact: HIGH
impactDescription: ensures correct controller unit testing via direct instantiation and precise ActionResult assertions
tags: csharp, tests, controller, aspnetcore, actionresult
---

## Controller Test Rules

Unit test ASP.NET Core controllers by **instantiating them directly** with substituted services and asserting on the returned `ActionResult` types. No web host, no HTTP.

### FORBIDDEN

- **FORBIDDEN** to use `WebApplicationFactory<T>` or `TestServer` in unit tests — that boots the full HTTP pipeline (integration testing, different rule set)

**Incorrect:**

```csharp
// Integration-level setup presented as a unit test
public class UserControllerTests : IClassFixture<WebApplicationFactory<Program>>
{
    [Fact]
    public async Task GetUser_ExistingId_Returns200()
    {
        var client = _factory.CreateClient(); // full pipeline - not a unit test
        var response = await client.GetAsync("/api/users/1");
        response.StatusCode.Should().Be(HttpStatusCode.OK);
    }
}
```

**Correct:**

```csharp
using FluentAssertions;
using Microsoft.AspNetCore.Mvc;
using NSubstitute;
using Xunit;

public class UserControllerTests
{
    private readonly IUserService _userService = Substitute.For<IUserService>();
    private readonly UserController _controller;

    public UserControllerTests()
    {
        _controller = new UserController(_userService);
    }

    [Fact]
    public void GetUser_ExistingId_ReturnsOkWithUser()
    {
        // Arrange
        var expectedUser = new User("1", "John", "john@test.com");
        _userService.FindById("1").Returns(expectedUser);

        // Act
        IActionResult actualResult = _controller.GetUser("1");

        // Assert
        User actualUser = actualResult.Should().BeOfType<OkObjectResult>()
            .Which.Value.Should().BeOfType<User>().Subject;
        actualUser.Id.Should().Be("1");
        actualUser.Name.Should().Be("John");
    }

    [Fact]
    public void GetUser_NonExistentId_ReturnsNotFound()
    {
        // Arrange
        _userService.FindById("999").Returns((User?)null);

        // Act
        IActionResult actualResult = _controller.GetUser("999");

        // Assert
        actualResult.Should().BeOfType<NotFoundResult>();
    }

    [Fact]
    public void CreateUser_ValidRequest_ReturnsCreatedAtAction()
    {
        // Arrange
        var request = new CreateUserRequest("John", "john@test.com");
        _userService.Create(Arg.Is<CreateUserRequest>(r => r.Email == "john@test.com"))
            .Returns(new User("1", "John", "john@test.com"));

        // Act
        IActionResult actualResult = _controller.CreateUser(request);

        // Assert
        var actualCreated = actualResult.Should().BeOfType<CreatedAtActionResult>().Subject;
        actualCreated.ActionName.Should().Be(nameof(UserController.GetUser));
        actualCreated.StatusCode.Should().Be(201);
    }

    [Fact]
    public void CreateUser_DuplicateEmail_ReturnsBadRequestWithMessage()
    {
        // Arrange
        var request = new CreateUserRequest("John", "taken@test.com");
        _userService.Create(Arg.Any<CreateUserRequest>())
            .Returns(x => throw new DuplicateEmailException("taken@test.com"));

        // Act
        IActionResult actualResult = _controller.CreateUser(request);

        // Assert
        actualResult.Should().BeOfType<BadRequestObjectResult>()
            .Which.Value.Should().Be("Email already registered: taken@test.com");
    }
}
```

Note on `ActionResult<T>`: when the action returns `ActionResult<T>`, assert on `actualResult.Result` (the wrapped `IActionResult`), e.g. `actualResult.Result.Should().BeOfType<OkObjectResult>()`.

### Separate Tests per Status Code

**Never merge** different 4xx outcomes into one test. Each of 400, 401, 403, 404 (and any other status the controller can return) gets its own test with its own name — a merged test hides which behavior broke.

```csharp
// WRONG - one test asserting "some 4xx happens" for several inputs
// CORRECT - GetUser_NonExistentId_ReturnsNotFound and
//           CreateUser_DuplicateEmail_ReturnsBadRequestWithMessage as separate [Fact]s
```

For 401/403: if the controller method itself returns `Unauthorized()`/`Forbid()`, unit test those branches separately. If auth is enforced only by `[Authorize]` attributes, see the pipeline limitation below — that enforcement is middleware behavior, an integration concern.

### [ApiController] Validation Limitation — Be Honest

With `[ApiController]`, the automatic `400 Bad Request` for invalid models happens in the **MVC pipeline before the action executes**. Calling the action directly in a unit test **bypasses it** — the action runs even with an invalid DTO, and no automatic 400 is produced.

- Do NOT write a unit test that passes an invalid DTO to the action and expects an automatic 400 — it tests nothing real
- Test validation attributes (`[Required]`, `[EmailAddress]`, ranges) separately via `Validator.TryValidateObject` on the DTO, or defer auto-400 behavior to integration tests
- Manual `ModelState` checks inside the action body (`if (!ModelState.IsValid) return BadRequest(ModelState);`) CAN be unit tested by seeding an error first:

```csharp
[Fact]
public void UpdateUser_InvalidModelState_ReturnsBadRequest()
{
    // Arrange - only valid when the action itself checks ModelState
    _controller.ModelState.AddModelError("Email", "Invalid email format");

    // Act
    IActionResult actualResult = _controller.UpdateUser("1", new UpdateUserRequest("", "bad"));

    // Assert
    actualResult.Should().BeOfType<BadRequestObjectResult>();
}
```

### What to Test in Controller Unit Tests

1. **Result type per branch**: `OkObjectResult`, `NotFoundResult`, `BadRequestObjectResult`, `CreatedAtActionResult`, `NoContentResult`
2. **Response payload**: assert fields of `.Value`, not just the type
3. **Status codes**: `((ObjectResult)actualResult).StatusCode.Should().Be(422);` for non-standard results
4. **Service interaction**: the right service method is called with the right arguments
5. **Exception mapping**: service exceptions caught by the action produce the intended result type (exceptions handled by exception-handling middleware are an integration concern)


---

## csharp-test-template.md

---
title: C# Test Template
impact: HIGH
impactDescription: ensures consistent test structure and prevents inappropriate test hosts
tags: csharp, tests, template, xunit, structure
---

## C# Test Template

Use xUnit with consistent structure. Keep unit tests fast — no web hosts, no containers, no DI containers.

### FORBIDDEN

- **FORBIDDEN** to use `WebApplicationFactory<T>` or `TestServer` in unit tests — these boot the ASP.NET Core pipeline (integration testing)
- **FORBIDDEN** to use Testcontainers (or any real database/broker) in unit tests
- **FORBIDDEN** to use `[Collection]` or shared class fixtures (`IClassFixture<T>`) to share **mutable** state between unit tests — each test must be independent

**Incorrect:**

```csharp
// Booting the whole web application for a unit test - slow, integration-level
public class CalculatorServiceTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;

    public CalculatorServiceTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory;
    }

    [Fact]
    public async Task Calculate_ValidInput_ReturnsResult()
    {
        var client = _factory.CreateClient();
        // ...
    }
}
```

**Correct:**

```csharp
using FluentAssertions;
using NSubstitute;
using Xunit;

namespace MyApp.Services.Tests;

public class CalculatorServiceTests
{
    private readonly IDependencyService _dependencyService = Substitute.For<IDependencyService>();
    private readonly CalculatorService _calculatorService;

    public CalculatorServiceTests()
    {
        _calculatorService = new CalculatorService(_dependencyService);
    }

    [Fact]
    public void Calculate_ValidInput_ReturnsResult()
    {
        // Arrange
        _dependencyService.GetValue().Returns(10);

        // Act
        int actualResult = _calculatorService.Calculate(5);

        // Assert
        int expectedResult = 15;
        actualResult.Should().Be(expectedResult);
    }

    [Fact]
    public void Calculate_NegativeInput_ThrowsArgumentException()
    {
        // Arrange-Act-Assert
        _calculatorService.Invoking(s => s.Calculate(-1))
            .Should().Throw<ArgumentException>()
            .WithMessage("Input must be positive*");
    }
}
```

### Constructor Is the Per-Test Setup

xUnit creates a **new instance of the test class for every test method**. The constructor therefore runs before each test — it IS the per-test setup mechanism. There is no `[SetUp]` attribute; do not look for one.

- Put substitute creation and SUT construction in field initializers and the constructor
- Instance fields never leak state between tests (fresh instance per test)
- For per-test teardown, implement `IDisposable`; for async setup/teardown, implement `IAsyncLifetime`

### [Fact] vs [Theory]

- `[Fact]` — a single scenario with fixed data. Default choice.
- `[Theory]` + `[InlineData(...)]` — the **same behavior** across multiple input values. Use only when the assertion logic is identical for every row; different outcomes (e.g., success vs. exception) belong in separate `[Fact]` tests.

```csharp
[Theory]
[InlineData(1, 1, 2)]
[InlineData(0, 5, 5)]
[InlineData(-3, 3, 0)]
public void Add_TwoOperands_ReturnsSum(int a, int b, int expectedSum)
{
    // Act
    int actualSum = _calculatorService.Add(a, b);

    // Assert
    actualSum.Should().Be(expectedSum);
}
```

### Basic Template Structure

```csharp
using FluentAssertions;
using NSubstitute;
using Xunit;

namespace {SutNamespace}.Tests;

public class {TestedClassName}Tests
{
    private readonly I{Dependency} _{dependency} = Substitute.For<I{Dependency}>();
    private readonly {TestedClassName} _{testedClassName};

    public {TestedClassName}Tests()
    {
        _{testedClassName} = new {TestedClassName}(_{dependency});
    }

    [Fact]
    public void {TestedMethod}_{GivenState}_{ExpectedOutcome}()
    {
        // Arrange
        // Act
        // Assert
    }
}
```

### Key Points

1. Place test files in `tests/{Project}.Tests/{ClassName}Tests.cs`; the test class name is `{ClassName}Tests`
2. Use the SUT's namespace with a `.Tests` suffix (e.g., `MyApp.Services` → `MyApp.Services.Tests`)
3. Test names use `Method_State_Outcome` in PascalCase — the C# rendering of `{method}_{state}_{outcome}`
4. Follow the Arrange-Act-Assert (AAA) pattern with `// Arrange`, `// Act`, `// Assert` comments — the .NET convention for the same structure Given-When-Then provides elsewhere in this repo; prefix result variables with `actual`/`expected`
5. Use AwesomeAssertions (`.Should()...`) for assertions — the package keeps the `FluentAssertions` namespace for drop-in compatibility, so `using FluentAssertions;` is correct
6. Substitute dependencies with NSubstitute (`Substitute.For<IInterface>()`), never the SUT itself


---

## domain-service-rules.md

---
title: Domain and Service Unit Test Rules
impact: HIGH
impactDescription: ensures fast, isolated unit tests for business logic
tags: csharp, tests, unit, domain, service, nsubstitute
---

## Domain and Service Unit Test Rules

Use NSubstitute for unit testing services and domain logic. Keep tests fast and isolated: construct the SUT directly with constructor injection.

### Rules

- Substitute collaborators as interfaces; pass them to the SUT via its constructor
- Do NOT build a DI container (`ServiceCollection` / `ServiceProvider`) or start any host in unit tests
- Substitute external dependencies, never the system under test
- Never substitute simple value objects — construct them for real

**Incorrect:**

```csharp
// Building a DI container for a unit test - slow, hides wiring
public class OrderServiceTests
{
    private readonly OrderService _orderService;

    public OrderServiceTests()
    {
        var services = new ServiceCollection();
        services.AddSingleton<IOrderRepository, OrderRepository>();
        services.AddSingleton<OrderService>();
        _orderService = services.BuildServiceProvider().GetRequiredService<OrderService>();
    }
}

// Substituting a value object - unnecessary
[Fact]
public void ProcessOrder_ValidOrder_CalculatesCorrectly()
{
    var product = Substitute.For<IProduct>();
    product.Price.Returns(100.0m);
    product.Name.Returns("Test");
    // ...
}
```

**Correct:**

```csharp
using FluentAssertions;
using NSubstitute;
using Xunit;

public class OrderServiceTests
{
    private readonly IOrderRepository _orderRepository = Substitute.For<IOrderRepository>();
    private readonly IPaymentService _paymentService = Substitute.For<IPaymentService>();
    private readonly INotificationService _notificationService = Substitute.For<INotificationService>();
    private readonly OrderService _orderService;

    public OrderServiceTests()
    {
        _orderService = new OrderService(_orderRepository, _paymentService, _notificationService);
    }

    [Fact]
    public void CreateOrder_ValidRequest_SavesAndReturnsOrder()
    {
        // Arrange
        var request = new OrderRequest("product-1", 5);
        var savedOrder = new Order("order-123", "product-1", 5);
        Order? capturedOrder = null;
        _orderRepository.Save(Arg.Do<Order>(o => capturedOrder = o)).Returns(savedOrder);

        // Act
        Order actualOrder = _orderService.CreateOrder(request);

        // Assert
        actualOrder.Id.Should().Be("order-123");
        capturedOrder.Should().NotBeNull();
        capturedOrder!.ProductId.Should().Be("product-1");
        capturedOrder.Quantity.Should().Be(5);
    }

    [Fact]
    public void ProcessPayment_ValidOrder_CallsPaymentService()
    {
        // Arrange
        var order = new Order("order-123", "product-1", 5) { Total = 500.0m };
        _paymentService.Charge("order-123", 500.0m).Returns(true);

        // Act
        bool actualResult = _orderService.ProcessPayment(order);

        // Assert
        actualResult.Should().BeTrue();
        _paymentService.Received(1).Charge("order-123", 500.0m);
    }

    [Fact]
    public void ProcessPayment_PaymentFails_ThrowsPaymentException()
    {
        // Arrange
        var order = new Order("order-123", "product-1", 5) { Total = 500.0m };
        _paymentService.Charge("order-123", 500.0m).Returns(false);

        // Act & Assert
        _orderService.Invoking(s => s.ProcessPayment(order))
            .Should().Throw<PaymentException>()
            .WithMessage("*Payment failed*");
    }

    [Fact]
    public void CalculateTotal_MultipleProducts_ReturnsSumOfPrices()
    {
        // Arrange - use real value objects
        var product1 = new Product("A", 50.0m);
        var product2 = new Product("B", 100.0m);
        var order = new Order(new List<Product> { product1, product2 });

        // Act
        decimal actualTotal = _orderService.CalculateTotal(order);

        // Assert
        decimal expectedTotal = 150.0m;
        actualTotal.Should().Be(expectedTotal);
    }
}
```

### What to Substitute vs What to Use Real Objects

**Substitute (as interfaces):**
- Repositories / data access
- HTTP/API clients (behind interfaces)
- Messaging producers / event publishers
- Cache services
- Any I/O operation (file system, clock, e-mail)

**Use Real Objects:**
- DTOs / records / value objects
- Domain entities (in most cases)
- Utility/static helper classes
- Mappers (usually)

### Exception Assertions

```csharp
// Synchronous
_orderService.Invoking(s => s.ProcessPayment(order))
    .Should().Throw<PaymentException>()
    .WithMessage("*Payment failed*");

// Asynchronous
await _orderService.Invoking(s => s.ProcessPaymentAsync(order))
    .Should().ThrowAsync<PaymentException>()
    .WithMessage("*Payment failed*");

// Asserting no exception
_orderService.Invoking(s => s.ProcessPayment(validOrder)).Should().NotThrow();
```

For `Received()` / `DidNotReceive()` verification and argument capture patterns, see `substitute-rules.md`.


---

## json-serialization.md

---
title: JSON Serialization in Tests
impact: HIGH
impactDescription: prevents test fragility and ensures explicit test data
tags: csharp, tests, json, serialization, raw-string-literals
---

## JSON Serialization in Tests

Use explicit JSON via C# raw string literals (`"""..."""`) instead of runtime serializers, so tests are deterministic and clearly show the expected data.

### Rules

- **DO NOT** call runtime serializers in tests to build request bodies or expected JSON — no `JsonSerializer.Serialize(...)` (System.Text.Json) and no `JsonConvert.SerializeObject(...)` (Newtonsoft.Json)
- You **MUST** use explicit raw string literals in stubs and assertions

**Incorrect:**

```csharp
[Fact]
public void ParseUser_ValidJson_ReturnsUser()
{
    // Using runtime serializer - fragile, hides the expected wire format
    var request = new UserRequest("John", "john@test.com");
    string requestJson = JsonSerializer.Serialize(request);

    User actualUser = _userParser.Parse(requestJson);

    actualUser.Name.Should().Be("John");
}

[Fact]
public void BuildPayload_ValidOrder_ProducesExpectedJson()
{
    // Serializing the expected value - comparing serializer to serializer proves nothing
    var expectedOrder = new Order("order-123", "product-1", 5);
    string expectedJson = JsonConvert.SerializeObject(expectedOrder);

    string actualJson = _payloadBuilder.Build(expectedOrder);

    actualJson.Should().Be(expectedJson);
}
```

**Correct:**

```csharp
[Fact]
public void ParseUser_ValidJson_ReturnsUser()
{
    // Arrange - explicit JSON literal: clear, deterministic
    string requestJson = """
        {
            "name": "John",
            "email": "john@test.com"
        }
        """;

    // Act
    User actualUser = _userParser.Parse(requestJson);

    // Assert
    actualUser.Name.Should().Be("John");
    actualUser.Email.Should().Be("john@test.com");
}

[Fact]
public async Task FetchData_ValidResponse_ParsesCorrectly()
{
    // Arrange - explicit stub response body (e.g., for a fake HttpMessageHandler)
    string responseJson = """
        {
            "status": "success",
            "data": { "value": 42 }
        }
        """;
    _httpHandler.SetResponse(HttpStatusCode.OK, responseJson);

    // Act
    DataResult actualResult = await _apiClient.FetchDataAsync();

    // Assert
    actualResult.Status.Should().Be("success");
    actualResult.Data.Value.Should().Be(42);
}
```

### Comparing Produced JSON

When the SUT itself produces JSON, assert against an explicit literal (parse both sides if formatting may differ):

```csharp
[Fact]
public void BuildPayload_ValidOrder_ProducesExpectedJson()
{
    // Arrange
    var order = new Order("order-123", "product-1", 5);

    // Act
    string actualJson = _payloadBuilder.Build(order);

    // Assert - expected structure spelled out, not regenerated by a serializer
    string expectedJson = """
        {"orderId":"order-123","productId":"product-1","quantity":5}
        """;
    JsonNode.Parse(actualJson)!.ToJsonString()
        .Should().Be(JsonNode.Parse(expectedJson)!.ToJsonString());
}
```

Note: `JsonNode.Parse` here is used for **whitespace-insensitive comparison** of two explicit literals/outputs — it does not violate the rule, which forbids *generating* expected data from objects at runtime.

### Benefits

1. **Readability** - Expected data is visible directly in the test
2. **Determinism** - No dependency on serializer options (naming policy, ordering, null handling)
3. **Debugging** - Easy to see exactly what wire format is being tested
4. **Maintenance** - Changing `JsonSerializerOptions` in production code cannot silently rewrite test expectations


---

## logging-rules.md

---
title: Logging Output Verification
impact: MEDIUM
impactDescription: enables reliable testing of log output and avoids the ILogger extension-method trap
tags: csharp, tests, logging, ilogger, fakelogger
---

## Logging Output Verification

Use `FakeLogger<T>` / `FakeLogCollector` from the `Microsoft.Extensions.Diagnostics.Testing` package to capture and assert log records.

### CRITICAL: The ILogger Extension-Method Trap

`LogInformation`, `LogWarning`, `LogError`, etc. are **static extension methods** that internally call `ILogger.Log(...)`. A substitute cannot intercept static extension methods, so verifying them on an `ILogger` substitute **does not work** — it either throws or verifies nothing meaningful.

**Incorrect:**

```csharp
[Fact]
public void ProcessOrder_Success_LogsOrderId()
{
    // Substituting ILogger and verifying an extension method - DOES NOT WORK.
    // LogInformation is a static extension; NSubstitute cannot intercept it.
    var logger = Substitute.For<ILogger<OrderService>>();
    var orderService = new OrderService(_orderRepository, logger);

    orderService.ProcessOrder(order);

    logger.Received(1).LogInformation("Processing order: order-123"); // broken verification
}
```

**Correct:**

```csharp
using FluentAssertions;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Testing;
using NSubstitute;
using Xunit;

public class OrderServiceTests
{
    private readonly IOrderRepository _orderRepository = Substitute.For<IOrderRepository>();
    private readonly FakeLogger<OrderService> _logger = new();
    private readonly OrderService _orderService;

    public OrderServiceTests()
    {
        _orderService = new OrderService(_orderRepository, _logger);
    }

    [Fact]
    public void ProcessOrder_Success_LogsOrderId()
    {
        // Arrange
        var order = new Order("order-123", "product-1", 5);

        // Act
        _orderService.ProcessOrder(order);

        // Assert
        FakeLogRecord actualRecord = _logger.Collector.GetSnapshot().Single();
        actualRecord.Level.Should().Be(LogLevel.Information);
        actualRecord.Message.Should().Contain("Processing order: order-123");
    }

    [Fact]
    public void ProcessOrder_InvalidOrder_LogsError()
    {
        // Arrange
        var invalidOrder = new Order(null!, "product-1", 5);

        // Act
        _orderService.Invoking(s => s.ProcessOrder(invalidOrder))
            .Should().Throw<ArgumentException>();

        // Assert
        IReadOnlyList<FakeLogRecord> actualRecords = _logger.Collector.GetSnapshot();
        actualRecords.Should().ContainSingle(r => r.Level == LogLevel.Error);
        actualRecords.Single(r => r.Level == LogLevel.Error)
            .Message.Should().Contain("Invalid order");
    }
}
```

### FakeLogCollector Essentials

```csharp
// FakeLogger<T> implements ILogger<T> - inject it directly into the SUT
var logger = new FakeLogger<OrderService>();

// All captured records (in order)
IReadOnlyList<FakeLogRecord> records = logger.Collector.GetSnapshot();

// Useful record properties
records[0].Level        // LogLevel.Information, Warning, Error, ...
records[0].Message      // the fully formatted message string
records[0].Exception    // the exception passed to Log, or null

// Latest record shortcut
logger.LatestRecord.Message.Should().Contain("expected message");

// Count assertions
logger.Collector.Count.Should().Be(2);
```

### Dependency Note

`FakeLogger<T>`, `FakeLogRecord`, and `FakeLogCollector` live in the **`Microsoft.Extensions.Diagnostics.Testing`** NuGet package (namespace `Microsoft.Extensions.Logging.Testing`). Add it to the test project if missing.

### Fallback Without the Package

If the project cannot add the package, write a small test double that implements `ILogger<T>` and captures `Log` calls — the non-generic `Log` method IS interceptable because it is the interface member:

```csharp
public sealed class CapturingLogger<T> : ILogger<T>
{
    public List<(LogLevel Level, string Message)> Entries { get; } = new();

    public IDisposable? BeginScope<TState>(TState state) where TState : notnull => null;
    public bool IsEnabled(LogLevel logLevel) => true;

    public void Log<TState>(LogLevel logLevel, EventId eventId, TState state,
        Exception? exception, Func<TState, Exception?, string> formatter)
        => Entries.Add((logLevel, formatter(state, exception)));
}
```

### Use Cases

1. **Verifying log messages** - ensure important events are logged with the right level
2. **Error logging** - verify exceptions are logged before being rethrown/swallowed
3. **Absence checks** - verify sensitive data is NOT logged (`records.Should().NotContain(...)`)


---

## substitute-rules.md

---
title: Argument Matching in NSubstitute
impact: HIGH
impactDescription: ensures meaningful verification of method arguments and prevents silent no-op substitutes
tags: csharp, tests, nsubstitute, argument-matching, verification
---

## Argument Matching in NSubstitute

Capture and verify actual arguments instead of using `Arg.Any<T>()` matchers for DTOs and model objects.

### Rules

- **Do NOT** use `Arg.Any<T>()` for DTO/model objects inside `Received()` verification
- Capture the real argument with `Arg.Do<T>(x => captured = x)` or match with `Arg.Is<T>(predicate)`, then assert the relevant fields

**Incorrect:**

```csharp
[Fact]
public void CreateOrder_ValidRequest_CallsRepository()
{
    // Arg.Any<Order>() - doesn't verify actual data passed
    _orderService.CreateOrder(new OrderRequest("product-1", 5));

    _orderRepository.Received().Save(Arg.Any<Order>());
}

[Fact]
public void NotifyUser_ValidUser_SendsEmail()
{
    // Arg.Any hides what's actually being sent
    _userService.NotifyUser(user);

    _emailService.Received().Send(Arg.Any<EmailMessage>());
}
```

**Correct:**

```csharp
[Fact]
public void CreateOrder_ValidRequest_SavesCorrectOrder()
{
    // Arrange
    var request = new OrderRequest("product-1", 5);
    Order? capturedOrder = null;
    _orderRepository.Save(Arg.Do<Order>(o => capturedOrder = o));

    // Act
    _orderService.CreateOrder(request);

    // Assert
    capturedOrder.Should().NotBeNull();
    capturedOrder!.ProductId.Should().Be("product-1");
    capturedOrder.Quantity.Should().Be(5);
}

[Fact]
public void NotifyUser_ValidUser_SendsCorrectEmail()
{
    // Arrange
    var user = new User("john@test.com", "John");

    // Act
    _userService.NotifyUser(user);

    // Assert - Arg.Is with a predicate on the fields that matter
    _emailService.Received(1).Send(Arg.Is<EmailMessage>(m =>
        m.To == "john@test.com" && m.Subject.Contains("John")));
}
```

### When `Arg.Any<T>()` Is Acceptable

Use `Arg.Any<T>()` only for:
- Primitive/simple types (`int`, `string`, `CancellationToken`) where the exact value doesn't matter
- Irrelevant arguments when the test's focus is on other behavior
- Pure existence checks (verifying the method was called at all)

```csharp
// OK - verifying call count, not data
_logger.Received(3).Log(Arg.Any<string>());

// OK - stubbing where the key value doesn't affect the test focus
_cache.Get(Arg.Any<string>()).Returns((CachedItem?)null);

// OK - CancellationToken is plumbing, not data
_repository.Received(1).SaveAsync(Arg.Is<Order>(o => o.Id == "order-123"), Arg.Any<CancellationToken>());
```

### CRITICAL: Substitute Interfaces, Not Concrete Classes

`Substitute.For<T>()` on a **concrete class** can only intercept `virtual`/`abstract` members. Calls to non-virtual members run the **real code** and `.Returns(...)` on them silently does nothing — no error, just a substitute that no-ops your configuration.

```csharp
// WRONG - Save() is non-virtual: Returns() is ignored, real Save() runs
var repository = Substitute.For<OrderRepository>();
repository.FindById("1").Returns(order); // silent no-op if FindById is non-virtual

// CORRECT - always substitute the interface
var repository = Substitute.For<IOrderRepository>();
repository.FindById("1").Returns(order);
```

- If the dependency has no interface, extract one (or wrap it) rather than substituting the concrete class
- **Never substitute the SUT itself** — the class under test must always be a real instance

### Verification Patterns

```csharp
// Verify a call happened exactly once (prefer explicit count)
_orderRepository.Received(1).Save(Arg.Is<Order>(o => o.ProductId == "product-1"));

// Verify a method was NOT called
_notificationService.DidNotReceive().Send(Arg.Any<EmailMessage>());

// Verify call count
_orderRepository.Received(2).FindById(Arg.Any<string>());

// Capture across multiple calls
var capturedOrders = new List<Order>();
_orderRepository.Save(Arg.Do<Order>(capturedOrders.Add));
_orderService.CreateOrders(requests);
capturedOrders.Should().HaveCount(2);
```


---

# TypeScript/JavaScript Rules

## assertion-rules.md

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
3. `objectContaining` only to trim irrelevant fields
4. No snapshots for logic — explicit assertions
5. No assertions inside conditionals/try-catch — use `toThrow`/`rejects` or `expect.assertions(n)`


---

## async-testing.md

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
it('pollStatus_becomesReady_resolvesWithStatus', async () => {
  // Given
  const actualPromise = poller.pollStatus(); // internally: setTimeout + await fetch

  // When — advances timers AND awaits resulting microtasks
  await vi.advanceTimersByTimeAsync(5000);
  // or run everything queued: await vi.runAllTimersAsync();

  // Then
  await expect(actualPromise).resolves.toBe('READY');
});
```

### Key Points

1. Every `rejects`/`resolves` assertion must be awaited — unawaited = silent pass
2. Match specific error types/messages in `rejects.toThrow(...)`
3. Success paths: `const actualResult = await service.method()`
4. "Does not reject" = just await it
5. No `done()` callbacks; no real timers — fake timers + `advanceTimersByTime[Async]`, restored in `afterEach`


---

## framework-detection.md

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
| `vitest.config.ts` / `vitest.config.js` / `vitest.config.mts` exists | Vitest |
| `vite.config.*` contains a `test` key | Vitest |
| `vitest` in `devDependencies` | Vitest |
| `jest.config.js` / `jest.config.ts` / `jest.config.json` exists | Jest |
| `"jest"` key in `package.json` | Jest |
| `jest` in `devDependencies` | Jest |

**If both are present** (e.g. during a migration): prefer the framework that has a config file. If both have config files or the signals are still ambiguous, ask the user which framework to target.

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
2. Both present → prefer the one with a config file; still ambiguous → ask the user
3. Use one framework's API consistently; the mapping table converts between them
4. Check `globals: true` (Vitest) or `@jest/globals` usage (Jest) to match import style


---

## mocking-rules.md

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

// vi.mocked() gives type-safe access to the auto-mocked import
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
  vi.restoreAllMocks();
});
```

Or set it once in config: `test: { restoreMocks: true }` (Vitest) / `restoreMocks: true` (Jest). If the project config already does this, don't duplicate the `afterEach`.

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
4. `vi.restoreAllMocks()` in `afterEach` (or `restoreMocks` config) — always
5. Never mock the SUT; assert mock arguments, not just call counts


---

## ts-test-template.md

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


---

# Post-Generation Rules

## compilation-verification.md

---
title: Post-Generation Compilation Verification
impact: HIGH
impactDescription: ensures generated tests compile successfully before delivery
tags: tests, compilation, verification, build, ci
---

## Post-Generation Compilation Verification

After generating test files, verify they compile successfully. Fix any issues before completing the task.

### Compilation Commands by Build System

| Build System | Command |
|--------------|---------|
| .NET | `dotnet build` |
| npm/yarn (TypeScript) | `npx tsc --noEmit` or `npm run build` |
| Python | `python -m py_compile <test_file>` |
| Go | `go build ./...` |
| Rust | `cargo check --tests` |
| Mix (Elixir) | `mix compile` |
| Swift | `swift build` |

### Process

1. **Create the test file** in the correct location
2. **Run compilation** using the appropriate command
3. **If compilation fails:**
   - Read the error message
   - Fix the issue (missing using directives, wrong dependencies, syntax errors)
   - Add missing dependencies to the appropriate config file
   - Re-run compilation
4. **Repeat until successful** (max 5 attempts)

### Common Issues and Fixes

**Missing Using Directives (C#):**
```csharp
// Error: The type or namespace name 'Fact' could not be found
// Fix: Add the missing using directives
using Xunit;
using NSubstitute;
using FluentAssertions;
```

**Missing Dependencies (.NET):**
```xml
<!-- Add to the test .csproj -->
<PackageReference Include="NSubstitute" Version="5.3.0" />
<PackageReference Include="AwesomeAssertions" Version="8.2.0" />
```

**Missing Dependencies (npm):**
```bash
# Add to devDependencies
npm install --save-dev vitest
```

**Wrong Namespace (C#):**
```csharp
// Error: The type or namespace name 'OrderService' could not be found
// Fix: Verify the namespace matches the SUT and the test project references the production project
namespace MyApp.Services.Tests; // Test project must have a ProjectReference to MyApp
```

**Type Mismatch (C#):**
```csharp
// Error: CS0029 cannot implicitly convert type
// Fix: Check return types and parameter types
// Wrong: actualResult.Should().Be("123");  // if actualResult is long
// Correct: actualResult.Should().Be(123L);
```

**Type Mismatch (TypeScript):**
```typescript
// Error: TS2345 Argument of type 'string' is not assignable to parameter of type 'number'
// Fix: Match the interface — read the actual type definitions, don't guess
```

### Verification Checklist

- [ ] Test file is in correct directory
- [ ] Namespace/module structure matches the project layout
- [ ] All using directives / imports are present and correct
- [ ] All dependencies are available
- [ ] No syntax errors
- [ ] Type compatibility is correct
- [ ] Compilation command succeeds

### Example Workflow

```bash
# 1. Create test file
# (using Write tool)

# 2. Run compilation
dotnet build

# 3. If errors, fix and retry
# Error: CS0246 The type or namespace name 'Substitute' could not be found
# Fix: Add the NSubstitute package reference

# 4. Verify success
dotnet build
# Build succeeded. 0 Warning(s). 0 Error(s).
```

**IMPORTANT:** Never deliver tests that don't compile. Always verify compilation before completing the task.


---

## test-execution-verification.md

---
title: Post-Generation Test Execution Verification
impact: HIGH
impactDescription: ensures generated tests actually pass, not just compile
tags: tests, execution, verification, pass, fail
---

## Post-Generation Test Execution Verification

After tests compile successfully, run them and verify they pass. Tests that compile but fail are not deliverable.

### Process

1. **Run only the generated test class** (not the entire test suite):

| Build System | Command |
|--------------|---------|
| .NET | `dotnet test --filter "FullyQualifiedName~{TestClassName}"` |
| Vitest | `npx vitest run {testFile}` |
| Jest | `npx jest {testFile}` or `npm test -- --testPathPattern={testFile}` |
| Python | `python -m pytest {test_file} -v` |
| Go | `go test -run {TestFuncName} ./...` |

2. **If any test fails:**
   - Read the failure output carefully
   - Identify the root cause (wrong expected value, incorrect substitute setup, missing stubbing, wrong method behavior assumption)
   - Fix the test — do NOT change the production code
   - Re-run to verify the fix
   - Repeat (max 3 fix attempts per failing test)

3. **If a test cannot be fixed after 3 attempts:**
   - Remove the failing test method
   - Add a `// TODO:` comment explaining what was intended and why it failed
   - Inform the user about the removed test

### Common Failure Causes and Fixes

**Wrong expected value (C#):**
```csharp
// Failure: Expected actualUser.Name to be "John Doe", but found "John"
// Fix: Read the production code to understand the actual return value
actualUser.Name.Should().Be("John"); // Match actual behavior
```

**Missing substitute stubbing (C#):**
```csharp
// Failure: NullReferenceException — substitute returned null/default
// Fix: Stub the methods the code path actually calls, before invoking the SUT
_repository.FindById("1").Returns(order); // Verify this is on the tested path
```

**Non-virtual member on a substituted class (C#):**
```csharp
// Failure: Returns() has no effect, real code runs instead
// Fix: Substitute the INTERFACE, not the concrete class — NSubstitute cannot
// intercept non-virtual members (see substitute-rules.md)
var repository = Substitute.For<IOrderRepository>();
```

**Unawaited async assertion (TypeScript):**
```typescript
// Failure symptom: test passes even when the code never rejects
// Fix: always await rejects/resolves assertions (see async-testing.md)
await expect(orderService.getOrder('missing')).rejects.toThrow(OrderNotFoundError);
```

**Mock state leaking between tests (TypeScript):**
```typescript
// Failure: test passes alone, fails in the suite (call counts off)
// Fix: restore mocks between tests
afterEach(() => {
  vi.restoreAllMocks();
});
```

### IMPORTANT

- Never deliver tests that fail. Passing tests are the minimum bar.
- Do NOT modify production code to make tests pass. Fix the tests instead.
- If the production code has a bug, the test should document the CURRENT behavior and add a comment noting the suspected bug.


---



---

# Part 4: AI Agent Workflow Specifications

This section details the exact workflows defined in the `SKILL.md` files that AI agents must follow when executing these skills.

## generate-tests SKILL.md

---
name: generate-tests
description: "Use when the user asks to generate, create, or write unit tests for code. Analyzes the target code, produces a structured test case list for review, then generates test code. Supports C#/.NET (xUnit, NSubstitute, AwesomeAssertions) and TypeScript/JavaScript (Vitest or Jest)."
allowed-tools: Read, Write, Glob, Grep, Bash, AskUserQuestion
context: fork
---

# Generate Tests Skill

You will analyze code and generate high-quality unit tests for a given target.

**Target to test:** $ARGUMENTS

## Quality Standards

- Take your time to analyze the code thoroughly before generating test cases.
- Quality is more important than speed — read all relevant source files and rules carefully.
- Do not skip any step in the workflow below. Every step exists for a reason.
- Do not take shortcuts with test data — read the actual classes to use correct constructors and fields.

---

## Instructions

### Step 1: Read Rules and Analyze Context

1. **Read the relevant rules** from `./rules/tests/` based on code type (see Rules Reference below)
2. **Read the target** source file/class/method
3. **Read dependencies**: Follow imports to read DTOs, entities, enums, custom exceptions, and other types referenced by the target (as specified in `code-context-analysis` rule)
4. **Check for existing tests**: Search for `{ClassName}Test` or `{ClassName}Tests` in the test directory (as specified in `existing-test-awareness` rule)
   - If found, read fully — you will add missing tests to it, not create a new file
   - If not found, scan 2-3 neighboring test classes to learn project conventions

### Step 2: Generate Test Cases

1. Analyze ALL code branches, including:
   - Success paths
   - Error/exception paths
   - Validation logic
   - Private/protected methods called by the target
   - Security annotations (if present)
2. Apply the INCLUDE/EXCLUDE rules strictly
3. Output the list of test cases in the format below — do NOT generate test code yet

#### Test Case Output Format

```
## Test Cases for {ClassName}.{methodName}

### 1. {testMethodName}
- **Given:** {preconditions/input state}
- **When:** {action being tested}
- **Then:** {expected outcome}
- **Code branch:** {which code path this covers}

### 2. {testMethodName}
...
```

#### Naming Convention
Test method name format: `{testedMethod}_{givenState}_{expectedOutcome}`

Examples:
- `calculateTotal_validProducts_returnsSum`
- `calculateTotal_emptyList_throwsIllegalArgumentException`
- `getUser_unauthorized_returns401`

Language renderings of the same convention:
- C#: `CalculateTotal_ValidProducts_ReturnsSum` (PascalCase segments)
- TypeScript / JavaScript: `calculateTotal_validProducts_returnsSum` (camelCase segments)

### Step 3: Ask for User Review

After outputting test cases, use the **AskUserQuestion tool** to ask the user:
```
Question: "Test cases are ready. Proceed with generating test code?"
Header: "Next step"
Options:
  - Label: "Yes, generate tests" / Description: "Proceed to generate test files from the test cases above"
  - Label: "No, let me review first" / Description: "Stop here so I can review and adjust the test cases"
```

- If user selects "Yes", proceed to Step 4
- If user selects "No", STOP and wait for further instructions

### Step 4: Generate Test Code

1. Determine the language (per `technology-stack-detection.md`), then the code type, and apply the matching rules:

   **C# / .NET** (`rules/tests/csharp/unit/`):
   - **Controller** → `controller-test-rules.md` (direct instantiation + ActionResult assertions; WebApplicationFactory FORBIDDEN)
   - **Service / Domain logic** → `domain-service-rules.md` (NSubstitute patterns, constructor injection)
   - **All C# code** → Always apply `csharp-test-template.md`, `substitute-rules.md`, `json-serialization.md`
   - **Structure comments**: use `// Arrange` / `// Act` / `// Assert` (AAA — the .NET convention), not `// Given/When/Then`

   **TypeScript / JavaScript** (`rules/tests/typescript/unit/` — applies to plain JS too):
   - **First** → `framework-detection.md` (Vitest vs Jest — never mix APIs)
   - **All TS/JS code** → Always apply `ts-test-template.md`, `mocking-rules.md`, `assertion-rules.md`; add `async-testing.md` when the target has async paths or timers

   **Any language, other code types** (Repository / Messaging / etc.) → apply that language's `domain-service-rules.md` (or closest baseline) and inform the user that type-specific rules are not yet available
2. If an existing test class was found in Step 1, add new test methods to it (do not create a duplicate file)
3. Generate tests following all rules and the test cases from Step 2
4. Create or update the test file using the Write tool

### Step 5: Verify Compilation and Execution

1. Run compilation and fix any issues (max 5 attempts — see `compilation-verification.md`)
2. Run the generated test class to verify all tests pass (see `test-execution-verification.md`)
3. Fix any failing tests — do NOT modify production code
4. If a test cannot be fixed after 3 attempts, remove it and inform the user

---

## Troubleshooting

### Target file not found
If the specified target does not exist, inform the user with the exact path you searched and ask for clarification.

### Unsupported language
If the target code is in a language without specific rules (not C#, TypeScript, or JavaScript), apply only the general rules and inform the user that language-specific conventions may need manual review.

### Compilation keeps failing
If compilation fails after 5 attempts:
1. Stop and show the user the remaining errors
2. Suggest possible causes (missing dependencies, incompatible versions)
3. Ask the user to resolve the build issue before continuing

### Tests fail due to production code behavior
If tests fail because the production code behaves differently than expected:
1. Do NOT modify production code
2. Fix the test to match actual behavior
3. If the behavior seems like a bug, add a comment: `// NOTE: current behavior may be a bug — {description}`

---

## Example

```
User says: "/generate-tests src/Services/OrderService.cs"

Step 1: Agent reads rules, reads OrderService.cs, reads OrderRequest.cs,
        Order.cs, IOrderRepository.cs (dependencies), checks for
        existing OrderServiceTests.cs

Step 2: Agent outputs 7 test cases covering:
        - CreateOrder success path
        - CreateOrder with invalid request (validation)
        - ProcessPayment success
        - ProcessPayment failure
        - CalculateTotal with products
        - CalculateTotal with empty list
        - CancelOrder for non-existent order

Step 3: Agent asks user to review. User says "Yes, generate tests".

Step 4: Agent generates OrderServiceTests.cs with NSubstitute substitutes for
        the repository and payment gateway, AAA structure, 7 test methods.

Step 5: Agent runs `dotnet test --filter "FullyQualifiedName~OrderServiceTests"`,
        all tests pass.

Result: Complete test file delivered with 7 passing tests.
```

---

## Rules Reference

**CRITICAL: You MUST read and apply all relevant rules from the `./rules/tests/` directory.**

> **Maintenance note:** General rules in `./rules/tests/general/` are shared with the `generate-test-cases` skill (which has copies in `rules/general/`). When updating rules, keep both locations in sync.

### General Rules (Always Apply)
- `general/test-case-generation-strategy.md` - INCLUDE/EXCLUDE criteria
- `general/naming-conventions.md` - Test naming format
- `general/general-principles.md` - Core testing principles (Given-When-Then, actual/expected)
- `general/technology-stack-detection.md` - Detect language and framework
- `general/what-makes-good-test.md` - Clarity, Completeness, Conciseness, Resilience
- `general/cleanly-create-test-data.md` - Use helpers and builders for test data
- `general/keep-cause-effect-clear.md` - Effects follow causes immediately
- `general/no-logic-in-tests.md` - KISS > DRY, avoid logic in assertions
- `general/keep-tests-focused.md` - One scenario per test
- `general/test-behaviors-not-methods.md` - Separate tests for behaviors
- `general/verify-relevant-arguments-only.md` - Only verify relevant mock arguments
- `general/prefer-public-apis.md` - Test public APIs over private methods
- `general/existing-test-awareness.md` - Check for existing tests, match project conventions
- `general/code-context-analysis.md` - Read dependencies before writing tests

### C# Unit Tests
- `csharp/unit/csharp-test-template.md` - xUnit template, FORBIDDEN patterns (WebApplicationFactory, Testcontainers)
- `csharp/unit/substitute-rules.md` - NSubstitute: capture DTOs with Arg.Do/Arg.Is, not Arg.Any
- `csharp/unit/json-serialization.md` - Raw string literals, no JsonSerializer.Serialize in tests
- `csharp/unit/logging-rules.md` - FakeLogger for log verification (ILogger extension-method trap)
- `csharp/unit/domain-service-rules.md` - NSubstitute patterns for services, constructor injection
- `csharp/unit/controller-test-rules.md` - Direct controller instantiation, ActionResult assertions

### TypeScript/JavaScript Unit Tests
- `typescript/unit/ts-test-template.md` - describe/it structure, typed test data
- `typescript/unit/framework-detection.md` - Vitest vs Jest detection and API mapping
- `typescript/unit/mocking-rules.md` - DI-first mocking, vi.mock hoisting pitfalls
- `typescript/unit/assertion-rules.md` - toBe/toEqual/toStrictEqual, snapshot tests FORBIDDEN for logic
- `typescript/unit/async-testing.md` - await rejects/resolves, fake timers, no done() callbacks

### Post-Generation
- `post-generation/compilation-verification.md` - Verify compilation
- `post-generation/test-execution-verification.md` - Verify tests pass


---

## generate-test-cases SKILL.md

---
name: generate-test-cases
description: "Use when the user asks to analyze code for test coverage, list what test cases are needed, or review testing strategy — WITHOUT generating actual test code."
allowed-tools: Read, Glob, Grep
context: fork
---

# Generate Test Cases Skill

You will analyze code and generate a list of test cases that should be written for a given method/class. This skill outputs test case descriptions only — it does NOT generate actual test code.

**Target to analyze:** $ARGUMENTS

## Quality Standards

- Take your time to analyze the code thoroughly before listing test cases.
- Quality is more important than speed — read all relevant source files and rules carefully.
- Do not skip reading the dependency classes. Understanding the full context produces better test cases.

---

## Instructions

### Step 1: Read Rules and Analyze Context

1. **Read the rules** from `./rules/general/` directory (see Rules Reference below)
2. **Read the target** source file/class/method specified above
3. **Read dependencies**: Follow imports to read DTOs, entities, enums, and other types referenced by the target (as specified in `code-context-analysis` rule)
4. **Check for existing tests**: Search for existing test classes covering this target (as specified in `existing-test-awareness` rule) — if found, read it fully and focus only on behaviors not yet covered

### Step 2: Generate Test Cases

1. Analyze ALL code branches, including:
   - Success paths
   - Error/exception paths
   - Validation logic
   - Private/protected methods called by the target
   - Security annotations (if present)
2. Apply the INCLUDE/EXCLUDE rules strictly
3. Output the list of test cases in the specified format
4. Do NOT generate actual test code — only the test case descriptions

---

## Output Format

For each test case, provide:

```
## Test Cases for {ClassName}.{methodName}

### 1. {testMethodName}
- **Given:** {preconditions/input state}
- **When:** {action being tested}
- **Then:** {expected outcome}
- **Code branch:** {which code path this covers}

### 2. {testMethodName}
...
```

### Naming Convention
Test method name format: `{testedMethod}_{givenState}_{expectedOutcome}`

Examples:
- C#: `CalculateTotal_ValidProducts_ReturnsSum` (PascalCase segments)
- C#: `CalculateTotal_EmptyList_ThrowsArgumentException`
- TypeScript/JavaScript: `getUser_unauthorized_returns401` (camelCase segments)
- TypeScript/JavaScript: `getUser_forbidden_returns403`

---

## Troubleshooting

### Target file not found
If the specified target does not exist, inform the user with the exact path you searched and ask for clarification.

### Unsupported language
If the target code is in a language without specific rules, apply only the general rules and inform the user.

### All behaviors already covered
If the existing test class already covers all identified behaviors, output a summary stating that coverage is complete. List what is already tested. Do not invent additional test cases to justify the analysis.

---

## Example

```
User says: "/generate-test-cases src/Services/OrderService.cs"

Step 1: Agent reads rules, reads OrderService.cs, reads OrderRequest.cs,
        Order.cs (dependencies), checks for existing OrderServiceTests.cs.

Step 2: Agent outputs:

## Test Cases for OrderService.CreateOrder

### 1. CreateOrder_ValidRequest_SavesAndReturnsOrder
- **Given:** Valid OrderRequest with ProductId "product-1" and Quantity 5
- **When:** CreateOrder is called
- **Then:** Order is saved to repository and returned with generated ID
- **Code branch:** Success path

### 2. CreateOrder_EmptyProductId_ThrowsArgumentException
- **Given:** OrderRequest with empty ProductId
- **When:** CreateOrder is called
- **Then:** ArgumentException is thrown
- **Code branch:** Validation — ProductId empty check
...
```

---

## Rules Reference

**CRITICAL: You MUST read and apply all rules from the following files before generating test cases:**

> **Maintenance note:** General rules in `./rules/general/` are shared with the `generate-tests` skill (which has copies in `rules/tests/general/`). When updating rules, keep both locations in sync.

### General Rules (Always Apply)
- `./rules/general/test-case-generation-strategy.md` - INCLUDE/EXCLUDE criteria for test cases
- `./rules/general/naming-conventions.md` - Test naming format
- `./rules/general/general-principles.md` - Core testing principles
- `./rules/general/what-makes-good-test.md` - Clarity, Completeness, Conciseness, Resilience
- `./rules/general/keep-tests-focused.md` - One scenario per test
- `./rules/general/test-behaviors-not-methods.md` - Separate tests for behaviors
- `./rules/general/prefer-public-apis.md` - Test public APIs over private methods
- `./rules/general/cleanly-create-test-data.md` - Use helpers and builders for test data
- `./rules/general/keep-cause-effect-clear.md` - Effects follow causes immediately
- `./rules/general/no-logic-in-tests.md` - KISS > DRY, avoid logic in assertions
- `./rules/general/technology-stack-detection.md` - Detect language and framework
- `./rules/general/verify-relevant-arguments-only.md` - Only verify relevant mock arguments
- `./rules/general/existing-test-awareness.md` - Check for existing tests, avoid duplicates
- `./rules/general/code-context-analysis.md` - Read dependencies before analyzing


---



---

# Part 5: Complete Google 'Testing on the Toilet' Reference Library

This section contains the core content extracted from all Google Testing on the Toilet blog posts referenced in the repository, ensuring no detail is lost.

## Testing On Toilet Tests Too Dry Make
**Source:** https://testing.googleblog.com/2019/12/testing-on-toilet-tests-too-dry-make.html

*Failed to fetch content.*

## Testing On Toilet Keep Tests Focused
**Source:** https://testing.googleblog.com/2018/06/testing-on-toilet-keep-tests-focused.html

*Failed to fetch content.*

## Increase Test Fidelity By Avoiding Mocks
**Source:** https://testing.googleblog.com/2024/02/increase-test-fidelity-by-avoiding-mocks.html

*Failed to fetch content.*

## Testing On Toilet Separation Of
**Source:** https://testing.googleblog.com/2020/12/testing-on-toilet-separation-of.html

*Failed to fetch content.*

## Testing On Toilet Testing Ui Logic
**Source:** https://testing.googleblog.com/2020/10/testing-on-toilet-testing-ui-logic.html

*Failed to fetch content.*

## Tech On Toilet Driving Software
**Source:** https://testing.googleblog.com/2024/12/tech-on-toilet-driving-software.html

*Failed to fetch content.*

## Testing On Toilet Only Verify Relevant
**Source:** https://testing.googleblog.com/2018/06/testing-on-toilet-only-verify-relevant.html

*Failed to fetch content.*

## Testing On Toilet Cleanly Create Test
**Source:** https://testing.googleblog.com/2018/02/testing-on-toilet-cleanly-create-test.html

*Failed to fetch content.*

## Testing On Toilet Exercise Service Call
**Source:** https://testing.googleblog.com/2018/11/testing-on-toilet-exercise-service-call.html

*Failed to fetch content.*

## Testing On Toilet Dont Mock Types You
**Source:** https://testing.googleblog.com/2020/07/testing-on-toilet-dont-mock-types-you.html

*Failed to fetch content.*

## Testing On Toilet What Makes Good End
**Source:** https://testing.googleblog.com/2016/09/testing-on-toilet-what-makes-good-end.html

*Failed to fetch content.*

## Testing On Toilet Change Detector Tests
**Source:** https://testing.googleblog.com/2015/01/testing-on-toilet-change-detector-tests.html

*Failed to fetch content.*

## Testing On Toilet Only Verify State
**Source:** https://testing.googleblog.com/2017/12/testing-on-toilet-only-verify-state.html

*Failed to fetch content.*

## Testing On Toilet Prefer Testing Public
**Source:** https://testing.googleblog.com/2015/01/testing-on-toilet-prefer-testing-public.html

*Failed to fetch content.*

## Testing On Toilet Keep Cause And Effect
**Source:** https://testing.googleblog.com/2017/01/testing-on-toilet-keep-cause-and-effect.html

*Failed to fetch content.*

## Testing On Toilet Risk Driven Testing
**Source:** https://testing.googleblog.com/2014/05/testing-on-toilet-risk-driven-testing.html

*Failed to fetch content.*

## Testing On Toilet Writing Descriptive
**Source:** https://testing.googleblog.com/2014/10/testing-on-toilet-writing-descriptive.html

*Failed to fetch content.*

## Testing On Toilet Test Behaviors Not
**Source:** https://testing.googleblog.com/2014/04/testing-on-toilet-test-behaviors-not.html

*Failed to fetch content.*

## Testing On Toilet Effective Testing
**Source:** https://testing.googleblog.com/2014/05/testing-on-toilet-effective-testing.html

*Failed to fetch content.*

## Testing On Toilet Dont Put Logic In
**Source:** https://testing.googleblog.com/2014/07/testing-on-toilet-dont-put-logic-in.html

*Failed to fetch content.*

## Testing On Toilet Test Behavior Not
**Source:** https://testing.googleblog.com/2013/08/testing-on-toilet-test-behavior-not.html

*Failed to fetch content.*

## Testing On Toilet Know Your Test Doubles
**Source:** https://testing.googleblog.com/2013/07/testing-on-toilet-know-your-test-doubles.html

*Failed to fetch content.*

## Testing On Toilet Fake Your Way To
**Source:** https://testing.googleblog.com/2013/06/testing-on-toilet-fake-your-way-to.html

*Failed to fetch content.*

## Testing On Toilet Dont Overuse Mocks
**Source:** https://testing.googleblog.com/2013/05/testing-on-toilet-dont-overuse-mocks.html

*Failed to fetch content.*

## Tott Making Perfect Matcher
**Source:** https://testing.googleblog.com/2009/10/tott-making-perfect-matcher.html

*Failed to fetch content.*

## Tott Contain Your Environment
**Source:** https://testing.googleblog.com/2008/11/tott-contain-your-environment.html

*Failed to fetch content.*

## Testing On Toilet Testing State Vs
**Source:** https://testing.googleblog.com/2013/03/testing-on-toilet-testing-state-vs.html

*Failed to fetch content.*

## Tott Contain Your Environment
**Source:** https://testing.googleblog.com/2008/10/tott-contain-your-environment.html

*Failed to fetch content.*

## Tott Simulating Time In Jsunit Tests
**Source:** https://testing.googleblog.com/2008/10/tott-simulating-time-in-jsunit-tests.html

*Failed to fetch content.*

## Tott Floating Point Comparison
**Source:** https://testing.googleblog.com/2008/10/tott-floating-point-comparison.html

*Failed to fetch content.*

## Tott Sleeping Synchronization
**Source:** https://testing.googleblog.com/2008/08/tott-sleeping-synchronization.html

*Failed to fetch content.*

## Tott 100 And Counting
**Source:** https://testing.googleblog.com/2008/08/tott-100-and-counting.html

*Failed to fetch content.*

## Tott Data Driven Traps
**Source:** https://testing.googleblog.com/2008/09/tott-data-driven-traps.html

*Failed to fetch content.*

## Progressive Developer Knows That In
**Source:** https://testing.googleblog.com/2008/08/progressive-developer-knows-that-in.html

*Failed to fetch content.*

## Tott Testing Against Interfaces
**Source:** https://testing.googleblog.com/2008/07/tott-testing-against-interfaces.html

*Failed to fetch content.*

## Tott Expect Vs Assert
**Source:** https://testing.googleblog.com/2008/07/tott-expect-vs-assert.html

*Failed to fetch content.*

## Tott Using Dependancy Injection To
**Source:** https://testing.googleblog.com/2008/05/tott-using-dependancy-injection-to.html

*Failed to fetch content.*

## Tott Friends You Can Depend On
**Source:** https://testing.googleblog.com/2008/06/tott-friends-you-can-depend-on.html

*Failed to fetch content.*

## Defeat Static Cling
**Source:** https://testing.googleblog.com/2008/06/defeat-static-cling.html

*Failed to fetch content.*

## Tott Invisible Branch
**Source:** https://testing.googleblog.com/2008/05/tott-invisible-branch.html

*Failed to fetch content.*

## Tott Testable Contracts Make
**Source:** https://testing.googleblog.com/2008/05/tott-testable-contracts-make.html

*Failed to fetch content.*

## Tott Avoiding Flakey Tests
**Source:** https://testing.googleblog.com/2008/04/tott-avoiding-flakey-tests.html

*Failed to fetch content.*

## Tott Time Is Random
**Source:** https://testing.googleblog.com/2008/04/tott-time-is-random.html

*Failed to fetch content.*

## Tott Testng On Toilet
**Source:** https://testing.googleblog.com/2008/03/tott-testng-on-toilet.html

*Failed to fetch content.*

## Tott Stroop Effect
**Source:** https://testing.googleblog.com/2008/02/tott-stroop-effect.html

*Failed to fetch content.*

## Tott Understanding Your Coverage Data
**Source:** https://testing.googleblog.com/2008/03/tott-understanding-your-coverage-data.html

*Failed to fetch content.*

## Tott Refactoring Tests In Red
**Source:** https://testing.googleblog.com/2007/04/tott-refactoring-tests-in-red.html

*Failed to fetch content.*

## In Movie Amadeus Austrian Emperor
**Source:** https://testing.googleblog.com/2008/02/in-movie-amadeus-austrian-emperor.html

*Failed to fetch content.*

## Tott Stubs Speed Up Your Unit Tests
**Source:** https://testing.googleblog.com/2007/04/tott-stubs-speed-up-your-unit-tests.html

*Failed to fetch content.*

## Tott Extracting Methods To Simplify
**Source:** https://testing.googleblog.com/2007/06/tott-extracting-methods-to-simplify.html

*Failed to fetch content.*

