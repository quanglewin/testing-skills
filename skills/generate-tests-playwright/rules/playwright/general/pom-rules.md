---
title: Page Object Model (POM) Rules
impact: HIGH
impactDescription: Keeps Playwright tests maintainable and separated from raw DOM selectors.
tags: tests, playwright, pom, architecture
---

## Page Object Model (POM) Rules

All Playwright UI tests must use the Page Object Model pattern. Tests should never contain raw CSS or XPath selectors.

### 1. Structure of a POM
- Create a class that encapsulates the page or component.
- Store locators as readonly fields initialized in the constructor.
- Expose methods for user actions (e.g., `SubmitForm()`).

**Example:**
```typescript
import { expect, type Locator, type Page } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly usernameInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.usernameInput = page.getByLabel('Username');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Sign in' });
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(user: string, pass: string) {
    await this.usernameInput.fill(user);
    await this.passwordInput.fill(pass);
    await this.submitButton.click();
  }
}
```

### 2. Tests should use the POM
- Tests should be clean and readable, orchestrating the Page Object.

**Correct Test:**
```typescript
import { test, expect } from '@playwright/test';
import { LoginPage } from './LoginPage';

test('valid login succeeds', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('testuser', 'password123');
  
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```
