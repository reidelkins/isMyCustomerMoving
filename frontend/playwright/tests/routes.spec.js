// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Routes', () => {
  test('/dashboard', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.getByTestId('welcome-message')).toHaveText(/Welcome/);
  });
  test('/dashboard/referrals', async ({ page }) => {
    await page.goto('/dashboard/referrals');
    await expect(page.getByTestId('welcome-message')).toHaveText(/Welcome/);
  }
});
