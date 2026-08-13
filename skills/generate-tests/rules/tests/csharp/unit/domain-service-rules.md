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

### Faking HttpClient

NSubstitute cannot mock `HttpClient` or `HttpMessageHandler` directly — `SendAsync` is `protected`, not interface-based, so there is nothing for the substitute to intercept. `Substitute.For<HttpClient>()` is **FORBIDDEN**. Prefer a typed-client abstraction (an interface your codebase owns) and substitute that; when the SUT takes `HttpClient` itself, use a small fake handler.

**Incorrect:**

```csharp
// FORBIDDEN - HttpClient's members are not substitutable; this silently runs real code
var httpClient = Substitute.For<HttpClient>();
```

**Correct:**

```csharp
// Small fake handler overriding the protected SendAsync
public sealed class FakeHttpMessageHandler : HttpMessageHandler
{
    private HttpResponseMessage _response = new(HttpStatusCode.OK);

    public void SetResponse(HttpStatusCode statusCode, string json) =>
        _response = new HttpResponseMessage(statusCode)
        {
            Content = new StringContent(json, Encoding.UTF8, "application/json")
        };

    protected override Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken) =>
        Task.FromResult(_response);
}

// In the test class: wrap the handler in a real HttpClient
private readonly FakeHttpMessageHandler _httpHandler = new();
private readonly ApiClient _apiClient;

public ApiClientTests()
{
    var httpClient = new HttpClient(_httpHandler) { BaseAddress = new Uri("https://test.local") };
    _apiClient = new ApiClient(httpClient);
}

[Fact]
public async Task FetchData_ServerReturnsOk_ReturnsParsedResult()
{
    // Arrange
    _httpHandler.SetResponse(HttpStatusCode.OK, """{ "value": 42 }""");

    // Act
    DataResult actualResult = await _apiClient.FetchDataAsync();

    // Assert
    actualResult.Value.Should().Be(42);
}
```

- Where the codebase already has a typed-client abstraction (e.g., `IWeatherApiClient`), substitute that interface instead of faking HTTP plumbing

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
