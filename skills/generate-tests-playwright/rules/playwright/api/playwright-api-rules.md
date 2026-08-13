---
title: Playwright API Rules
impact: MEDIUM
impactDescription: Standardizes testing backend API routes with Playwright.
tags: tests, playwright, api
---

## Playwright API Rules

Playwright is excellent for API testing using `request` from the test context.

### 1. Usage
- Use the `request` fixture provided by Playwright.

**Correct:**
```typescript
import { test, expect } from '@playwright/test';

test('GET /api/users returns 200 and data', async ({ request }) => {
  const response = await request.get('/api/users');
  expect(response.ok()).toBeTruthy();
  
  const data = await response.json();
  expect(data).toHaveProperty('users');
});
```

### 2. Asserting Status Codes
- Always assert the status code before attempting to parse the body to ensure clear failure messages.
- Use `expect(response.status()).toBe(200)` for exact matching, or `response.ok()` for any 2xx.
