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
_auditTrail.Received(3).Record(Arg.Any<string>());

// OK - stubbing where the key value doesn't affect the test focus
_cache.Get(Arg.Any<string>()).Returns((CachedItem?)null);

// OK - CancellationToken is plumbing, not data
_repository.Received(1).SaveAsync(Arg.Is<Order>(o => o.Id == "order-123"), Arg.Any<CancellationToken>());
```

Note: never substitute or verify `ILogger`/`ILogger<T>` this way — anything logging-related must follow `logging-rules.md` (`FakeLogger`).

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
