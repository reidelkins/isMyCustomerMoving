// @ts-check
const { test, expect } = require('@playwright/test');

test('login form', async ({ page }) => {
  await page.goto('/dashboard');

  await expect(page.getByTestId('welcome-message')).toHaveText(/Welcome/);
});