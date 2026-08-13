---
title: Cleanly Create Test Data
impact: HIGH
impactDescription: improves test readability and maintainability through clean data setup
tags: tests, test-data, helpers, builders, readability
---

## Cleanly Create Test Data

Use helper functions and builder patterns to create test data cleanly. Avoid cluttering tests with irrelevant details.

### Use Helper Functions

Helper functions hide irrelevant details and make tests easier to read.

**Incorrect:**

```csharp
[Fact]
public void CalculateTotal_MultipleItems_HappyPath()
{
    ShoppingCart shoppingCart = new ShoppingCart(new DefaultRoundingStrategy(),
        "unused", Mode.Normal, false, false, TimeZoneInfo.Utc, null);
    int totalPrice = shoppingCart.CalculateTotal(
        NewItem1(),
        NewItem2(),
        NewItem3());
    totalPrice.Should().Be(25); // Where did this number come from?
}
```

**Correct:**

```csharp
[Fact]
public void CalculateTotal_MultipleItems_HappyPath()
{
    ShoppingCart shoppingCart = NewShoppingCart();

    int actualTotal = shoppingCart.CalculateTotal(
        NewItemWithPrice(10),
        NewItemWithPrice(10),
        NewItemWithPrice(5));

    int expectedTotal = 25;
    actualTotal.Should().Be(expectedTotal);
}
```

### Use the Test Data Builder Pattern

When helper methods grow with many parameters, use the builder pattern.

**Incorrect:**

```csharp
// Helper methods become unwieldy with many parameters
Company small = NewCompany(2, 2, null, CompanyType.Public);
Company privatelyOwned = NewCompany(null, null, null, CompanyType.Private);
Company bankrupt = NewCompany(null, null, PastDate, CompanyType.Public);
```

**Correct:**

```csharp
Company small = NewCompany().WithEmployeesCount(2).WithBoardMembersCount(2).Build();
Company privatelyOwned = NewCompany().WithType(CompanyType.Private).Build();
Company bankrupt = NewCompany().WithBankruptcyDate(PastDate).Build();
Company arbitraryCompany = NewCompany().Build();

// Helper returns builder with required defaults
private static CompanyBuilder NewCompany()
{
    return new CompanyBuilder().WithType(CompanyType.Public);
}
```

### Never Rely on Default Values from Helpers

If a test depends on a value, explicitly set it even if it matches the helper's default.

**Incorrect:**

```csharp
private static CompanyBuilder NewCompany()
{
    return new CompanyBuilder().WithType(CompanyType.Public);
}

[Fact]
public void Test_PublicCompany()
{
    // Relies on helper's default - fragile!
    Company company = NewCompany().Build();
    // ...
}
```

**Correct:**

```csharp
[Fact]
public void Test_PublicCompany()
{
    // Explicitly set the value this test depends on
    Company company = NewCompany()
        .WithType(CompanyType.Public)  // Explicit even if matches default
        .WithBoardMembersCount(0)
        .Build();
    // ...
}
```

### Helper Function Guidelines

1. **Name helpers descriptively** - `CreateProductWithCategory("Office")` not `CreateProduct()`
2. **Only expose relevant parameters** - hide irrelevant details
3. **Keep helpers simple** - no business logic
4. **Consider builders for complex objects** - when many field combinations are needed
