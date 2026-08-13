---
title: Code Context Analysis
impact: HIGH
impactDescription: ensures correct test data by understanding the full dependency graph
tags: tests, context, dependencies, dto, entity, analysis
---

## Code Context Analysis

Before generating tests, read all types referenced by the target code. Tests that use wrong constructors, miss required fields, or create invalid objects will fail at compile time or produce meaningless results.

### What to Read Before Writing Tests

After reading the target class, identify and read:

1. **Direct parameter types**: Every class used as a method parameter
2. **Return types**: Every class returned by the method under test
3. **Field types injected via constructor**: Dependencies that need substituting
4. **Domain entities / DTOs**: Classes created or transformed in the method body
5. **Enums**: Any enum used in conditionals, switch statements/expressions, or as parameters
6. **Custom exceptions**: Exception classes thrown by the method
7. **Validators / Constraints**: Custom attribute classes if validation is tested

### Why This Matters

**Without reading dependencies:**
```csharp
// Compiles but FAILS - wrong constructor args
var request = new OrderRequest("product-1", 5);
// Actual constructor: OrderRequest(string productId, int quantity, string customerId)
```

**With reading dependencies:**
```csharp
// Correct - matches the actual constructor
var request = new OrderRequest("product-1", 5, "customer-123");
```

### How to Read Dependencies Efficiently

1. Read the target class's using directives and namespace to identify referenced types
2. Use Glob to find the source files: `**/OrderRequest.cs`
3. Read each dependency to understand:
   - Constructor parameters (types and order)
   - Required fields vs optional fields
   - Builder patterns (if present — use the builder)
   - Factory methods (if present — prefer over constructors)
   - Enum values available

### Pay Special Attention To

- **Object construction patterns**: records (positional constructors), `required` members, `init`-only setters, primary constructors, and static factory methods change how objects are constructed
- **Validation attributes**: `[Required]`, `[StringLength]`, `[Range]` on properties indicate constraints that tests should satisfy (or intentionally violate for negative tests)
- **Inheritance**: If a class extends another, read the parent class too
- **Generics**: Understand the type parameters to use correct types in tests

### Checklist

Before writing any test method:
- [ ] Read all parameter types used by the target method
- [ ] Read all return types
- [ ] Read domain entities created or modified in the method body
- [ ] Read enum classes used in conditionals
- [ ] Identified constructors, builders, or factory methods for test data creation
