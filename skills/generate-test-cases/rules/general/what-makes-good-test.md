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
