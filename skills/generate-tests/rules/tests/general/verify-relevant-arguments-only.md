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
