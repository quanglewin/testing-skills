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
