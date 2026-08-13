---
title: Prefer Testing Public APIs Over Private Methods
impact: HIGH
impactDescription: creates resilient tests that survive refactoring
tags: tests, public-api, private-methods, refactoring, resilience
---

## Prefer Testing Public APIs Over Private Methods

Test the public interface of your code. Private methods and implementation-detail classes should be tested indirectly through public APIs.

### Problem: Testing Implementation Details

**Incorrect:**

```csharp
// Testing private helper class directly
public class UserInfoValidatorTests
{
    [Fact]
    public void Validate_FutureDateOfBirth_ThrowsException()
    {
        UserInfoValidator validator = new UserInfoValidator();

        validator.Invoking(v => v.Validate(InfoWithFutureDob()))
            .Should().Throw<ValidationException>();
    }
}

// This test is fragile - if we inline or rename the validator, test breaks
```

**Correct:**

```csharp
// Test through the public API
public class UserInfoServiceTests
{
    [Fact]
    public void Save_FutureDateOfBirth_ThrowsValidationException()
    {
        UserInfoService service = new UserInfoService();
        UserInfo info = CreateUserInfo().WithDateOfBirth(FutureDate).Build();

        service.Invoking(s => s.Save(info))
            .Should().Throw<ValidationException>()
            .WithMessage("Invalid date of birth");
    }

    [Fact]
    public void Save_ValidInfo_PersistsToDatabase()
    {
        UserInfoService service = new UserInfoService();
        UserInfo info = CreateUserInfo().WithDateOfBirth(PastDate).Build();

        service.Save(info);

        _database.FindById(info.Id).Should().NotBeNull();
    }
}
```

### When to Test Private/Internal Classes

Test implementation classes separately only when:
1. **Reused across multiple public APIs** - becomes part of the public contract
2. **Complex enough to warrant isolation** - but consider if it should be extracted
3. **Third-party integration** - adapters that wrap external libraries

When a C# class is `internal` and genuinely needs direct testing, the mechanism is `[assembly: InternalsVisibleTo("TestProject")]` (typically an `<InternalsVisibleTo Include="TestProject" />` item) — never make the class public or access it via reflection instead. Note the attribute lives in the **production** project: if it is not already present, ask the user for approval before adding it — test-generation workflows must not modify production projects without explicit consent.

### Refactoring Freedom

Testing public APIs allows refactoring without changing tests:

```csharp
// Original implementation
public class UserInfoService
{
    private readonly UserInfoValidator _validator = new UserInfoValidator();

    public void Save(UserInfo info)
    {
        _validator.Validate(info);
        WriteToDatabase(info);
    }
}

// Refactored - validator inlined
public class UserInfoService
{
    public void Save(UserInfo info)
    {
        if (info.DateOfBirth.IsInFuture())
        {
            throw new ValidationException("Invalid date of birth");
        }
        WriteToDatabase(info);
    }
}

// Tests don't change because they test the public API!
```

### Guidelines

1. **Test behavior, not implementation** - focus on what, not how
2. **Use public methods as entry points** - even for testing edge cases
3. **Private methods are implementation** - should be covered by public method tests
4. **Consider visibility carefully** - if something needs direct testing, maybe it should be public
