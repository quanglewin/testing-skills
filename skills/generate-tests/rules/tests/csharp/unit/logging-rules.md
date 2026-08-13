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
