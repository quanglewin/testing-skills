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
