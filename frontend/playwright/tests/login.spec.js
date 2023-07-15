// @ts-check
const { test, expect } = require('@playwright/test');

test.beforeEach(async ({ page }) => {
  // Logout
  await page.goto('/dashboard');
  await page.getByTestId('profile-button').click();
  await page.getByRole('menuitem', { name: /logout/i }).click();
  await expect(page).toHaveURL(/.*logout/);

  // Got to login page
  await page.goto('/login');
});

test.describe('Login', () => {
  test('login with correct email and password', async ({ page }) => {
    // Fill out the form
    const email = process.env.TEST_LOGIN_EMAIL ? process.env.TEST_LOGIN_EMAIL : '';
    const password = process.env.TEST_LOGIN_PASSWORD ? process.env.TEST_LOGIN_PASSWORD : '';
    await page.getByLabel('email').fill(email);
    await page.getByLabel('password').fill(password);

    //  Submit the form
    await page.getByRole('button', { name: /login/i }).click();

    // Expects the URL to contain intro.
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test('login with wrong password', async ({ page }) => {
    // Fill out the form
    const email = process.env.TEST_LOGIN_EMAIL ? process.env.TEST_LOGIN_EMAIL : '';
    await page.getByLabel('email').fill(email);
    await page.getByLabel('password').fill('wrongpassword');

    //  Submit the form
    await page.getByRole('button', { name: /login/i }).click();

    // Expects the URL to contain intro.
    await expect(page).toHaveURL(/.*login/);
  });
});
