---
title: Don't Put Logic in Tests
impact: HIGH
impactDescription: prevents bugs in tests and makes expected values obvious
tags: tests, simplicity, kiss, no-logic, readability
---

## Don't Put Logic in Tests

Tests should be straightforward with no conditional logic, loops, or string concatenation. Keep expected values explicit and literal.

### KISS > DRY in Tests

Simplicity is more important than avoiding duplication in tests.

### Problem: Logic Hides Bugs

**Incorrect:**

```csharp
[Fact]
public void GetPhotosPageUrl()
{
    string baseUrl = "http://photos.google.com/";
    UrlBuilder urlBuilder = new UrlBuilder(baseUrl);

    string photosPageUrl = urlBuilder.GetPhotosPageUrl();

    // Bug hidden by concatenation: results in "//u/0/photos"
    photosPageUrl.Should().Be(baseUrl + "/u/0/photos");
}
```

**Correct:**

```csharp
[Fact]
public void GetPhotosPageUrl_HappyPath()
{
    UrlBuilder urlBuilder = new UrlBuilder("http://photos.google.com/");

    string actualUrl = urlBuilder.GetPhotosPageUrl();

    // Explicit literal - bug is obvious: "http://photos.google.com//u/0/photos"
    actualUrl.Should().Be("http://photos.google.com/u/0/photos");
}
```

### Avoid These Patterns in Tests

**Incorrect:**

```csharp
// Loops in tests
for (int i = 0; i < users.Count; i++)
{
    users[i].IsActive.Should().BeTrue();
}

// Conditionals in tests
if (response.IsSuccessful)
{
    response.Body.Should().NotBeNull();
}

// String concatenation in assertions
result.Should().Be("Hello, " + userName + "!");

// Calculations in assertions
total.Should().Be(price * quantity + tax);
```

**Correct:**

```csharp
// Explicit assertions
users.Should().OnlyContain(u => u.IsActive);

// No conditionals - test specific scenarios
response.IsSuccessful.Should().BeTrue();
response.Body.Should().NotBeNull();

// Literal expected values
result.Should().Be("Hello, John!");

// Pre-calculated expected values
int expectedTotal = 115; // 100 * 1 + 15 tax, calculated outside test
total.Should().Be(expectedTotal);
```

### When Logic is Necessary

If tests need complex logic, move it to helper functions with their own tests:

```csharp
// Helper with its own test coverage
public static class TestDataGenerator
{
    public static string GenerateExpectedGreeting(User user, DateOnly date)
    {
        // Complex logic here
    }
}

// TestDataGeneratorTests verifies this helper works correctly
```

### Key Principles

1. **Use literal values** - not computed values
2. **Avoid operators** - no `+`, `*`, string concatenation in assertions
3. **No control flow** - no `if`, `for`, `while` in test bodies
4. **KISS over DRY** - repetition is OK if it makes tests clearer
