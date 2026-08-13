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
        // Arrange
        int invalidInput = -1;

        // Act & Assert
        _calculatorService.Invoking(s => s.Calculate(invalidInput))
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
5. Exception tests combine the last two phases: use a separate `// Arrange` section, then `// Act & Assert` on the `Should().Throw...` expression (see `Calculate_NegativeInput_ThrowsArgumentException` above and `domain-service-rules.md`)
6. Use AwesomeAssertions (`.Should()...`) for assertions — the package keeps the `FluentAssertions` namespace for drop-in compatibility, so `using FluentAssertions;` is correct
7. Substitute dependencies with NSubstitute (`Substitute.For<IInterface>()`), never the SUT itself
8. Test methods for async SUT members must be declared `async Task` — `async void` test methods are **FORBIDDEN** (failures escape the test runner)
9. Never assert the value of a `Guid` the SUT generates internally — it is nondeterministic. Inject an ID-generator abstraction (e.g., `IIdGenerator`) and stub it, or capture the generated value with `Arg.Do` and assert on how the captured value is used
