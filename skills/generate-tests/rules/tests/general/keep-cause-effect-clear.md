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
