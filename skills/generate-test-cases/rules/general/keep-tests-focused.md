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
