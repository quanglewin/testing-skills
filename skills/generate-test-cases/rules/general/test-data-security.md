---
title: Test Data Security
impact: HIGH
impactDescription: prevents secrets, PII, and production references from leaking into committed test code
tags: tests, security, secrets, pii, test-data, compliance
---

## Test Data Security

Generated test code gets committed and reviewed like any other code. It must never contain real secrets, real personal data, or references to production systems.

### 1. Never Use Real Credentials or Secrets

Use obvious placeholders for passwords, API keys, tokens, and connection strings. Never copy values from configuration files, environment variables, `.env` files, or user-provided examples that could be real.

**Incorrect:**

```csharp
// Copied from appsettings.json — may be a real key
var client = new PaymentClient("sk_live_51Hxk2eF9aBcDeFgH");
```

**Correct:**

```csharp
var client = new PaymentClient("test-api-key");
```

Also avoid fabricating strings that MATCH real secret formats (e.g. `AKIA...` AWS key patterns, `sk_live_...` Stripe patterns, JWT-shaped strings signed with anything meaningful) — they trip secret scanners and trigger false security incidents. Plain placeholders like `"test-api-key"` or `"fake-token"` are best.

### 2. Never Reference Production Systems

Test data must not contain production hostnames, internal service URLs, real database connection strings, or real queue/topic names taken from configuration.

**Incorrect:**

```typescript
const gateway = new HttpGateway('https://payments.internal.mycompany.com');
```

**Correct:**

```typescript
const gateway = new HttpGateway('https://payments.example.com');
```

Use `example.com`, `localhost`, or clearly fake hosts. In unit tests the URL should never be dialed anyway — network calls are mocked.

### 3. Use Clearly Fake Personal Data

Never copy records from production databases, real log output, or bug reports containing customer data into fixtures. Use generic fake identities.

- Names: `John Doe`, `Jane Smith`
- Emails: `john@test.com`, `user@example.com`
- Phone numbers: reserved fake ranges (e.g. `+1-555-0100`)
- IDs: obviously synthetic (`"user-1"`, `Guid.Parse("00000000-0000-0000-0000-000000000001")`)

### 4. Unit Tests Must Not Read Real Configuration

A unit test that reads `Environment.GetEnvironmentVariable("DB_PASSWORD")` or loads `.env` is coupled to secrets and to the machine it runs on. Inject configuration as plain fake values instead.

**Incorrect:**

```typescript
const apiKey = process.env.PAYMENT_API_KEY; // real secret pulled into the test run
const service = new PaymentService(apiKey);
```

**Correct:**

```typescript
const service = new PaymentService('test-api-key');
```

### Checklist Before Delivering Tests

- [ ] No values copied from config files, `.env`, or environment variables
- [ ] No strings matching real secret formats (cloud keys, `sk_live_`, JWTs)
- [ ] No production hostnames, connection strings, or internal URLs
- [ ] No real customer/user data in fixtures
- [ ] Tests make no network calls and read no real configuration
