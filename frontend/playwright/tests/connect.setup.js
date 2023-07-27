import { test as setup, expect } from '@playwright/test';

setup('connect to web server', async ({ page }) => {
  await page.goto('/login');
  await expect(page).toHaveURL(/.*login/);
  await expect(page).toHaveTitle(/Login/);
});