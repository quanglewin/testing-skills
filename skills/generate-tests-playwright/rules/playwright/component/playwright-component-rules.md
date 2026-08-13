---
title: Playwright Component Rules
impact: HIGH
impactDescription: Best practices for testing React/Vue/Svelte components in Playwright.
tags: tests, playwright, component, ui
---

## Playwright Component Rules

When testing components via Playwright Component Testing (`@playwright/experimental-ct-*`):

### 1. Web-First Assertions
- Use `expect(locator).toBeVisible()`, `.toHaveText()`, etc.
- Never use generic assertions like `expect(await locator.isVisible()).toBe(true)`. Playwright needs web-first assertions to auto-retry and avoid flakiness.

**Incorrect:**
```typescript
const isVisible = await page.getByText('Success').isVisible();
expect(isVisible).toBe(true);
```

**Correct:**
```typescript
await expect(page.getByText('Success')).toBeVisible();
```

### 2. Auto-Waiting
- **NEVER** use `page.waitForTimeout()`.
- Use web-first assertions which automatically wait for the element to reach the expected state.

### 3. Locators
- Prefer user-facing locators: `getByRole`, `getByText`, `getByLabel`.
- Avoid CSS selectors (`.btn-primary`) or XPath, as they break easily during refactoring.

**Correct:**
```typescript
await component.getByRole('button', { name: 'Submit' }).click();
```
