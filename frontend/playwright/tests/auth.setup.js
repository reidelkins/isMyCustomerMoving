import { test as setup, expect } from '@playwright/test';
import { TEST_LOGIN_EMAIL, TEST_LOGIN_PASSWORD } from './utils/constants';

const authFile = 'playwright/.auth/user.json';

setup('authenticate', async ({ page }) => {
  // Perform authentication
  await page.goto('/login');
  const email = TEST_LOGIN_EMAIL;
  const password = TEST_LOGIN_PASSWORD;
  await page.getByLabel('email').fill(email);
  await page.getByLabel('password').fill(password);
  await page.getByRole('button', {name: /login/i}).click();
  // Wait until the page receives the cookies.
  //
  // Sometimes login flow sets cookies in the process of several redirects.
  // Wait for the final URL to ensure that the cookies are actually set.
  await page.waitForURL('/dashboard');
  // Alternatively, you can wait until the page reaches a state where all cookies are set.
  await expect(page.getByTestId('welcome-message')).toHaveText(/Welcome/);

  // Export the cookies to a file.
  await page.context().storageState({ path: authFile });
});