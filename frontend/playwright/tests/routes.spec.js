// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Routes exist and have titles', () => {
  test('/dashboard', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveTitle(/Home/);
    await expect(page.getByTestId('welcome-message')).toHaveText(/Welcome/);
  });
  test('/dashboard/customers', async ({ page }) => {
    await page.goto('/dashboard/customers');
    await expect(page).toHaveTitle(/Customer Data/);
  });
  test('/dashboard/referrals', async ({ page }) => {
    await page.goto('/dashboard/referrals');
    await expect(page).toHaveTitle(/Referrals/);
  });
  test('/dashboard/forsale', async ({ page }) => {
    await page.goto('/dashboard/forsale');
    await expect(page).toHaveTitle(/For Sale/);
  });
  test('/dashboard/recentlysold', async ({ page }) => {
    await page.goto('/dashboard/recentlysold');
    await expect(page).toHaveTitle(/Recently Sold/);
  });
  test('/dashboard/settings/user', async ({ page }) => {
    await page.goto('/dashboard/settings/user');
    await expect(page).toHaveTitle(/Profile Settings/);
  });
  test('/dashboard/settings/enterprise', async ({ page }) => {
    await page.goto('/dashboard/settings/enterprise');
    await expect(page).toHaveTitle(/Enterprise Settings/);
  });
});

test.describe('Ensure routes are protected', () => {
  /*
  Logout before hitting protected routes
  */
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard');
    await page.getByTestId('profile-button').click();
    await page.getByRole('menuitem', { name: /logout/i }).click();
    await expect(page).toHaveURL(/.*logout/);
  });

  test('protected /dashboard', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/.*login/);
  });
  test('protected /dashboard/customers', async ({ page }) => {
    await page.goto('/dashboard/customers');
    await expect(page).toHaveURL(/.*login/);
  });
  test('protected /dashboard/referrals', async ({ page }) => {
    await page.goto('/dashboard/referrals');
    await expect(page).toHaveURL(/.*login/);
  });
  test('protected /dashboard/forsale', async ({ page }) => {
    await page.goto('/dashboard/forsale');
    await expect(page).toHaveURL(/.*login/);
  });
  test('protected /dashboard/recentlysold', async ({ page }) => {
    await page.goto('/dashboard/recentlysold');
    await expect(page).toHaveURL(/.*login/);
  });
  test('protected /dashboard/settings/user', async ({ page }) => {
    await page.goto('/dashboard/settings/user');
    await expect(page).toHaveURL(/.*login/);
  });
  test('protected /dashboard/settings/enterprise', async ({ page }) => {
    await page.goto('/dashboard/settings/enterprise');
    await expect(page).toHaveURL(/.*login/);
  });
});
