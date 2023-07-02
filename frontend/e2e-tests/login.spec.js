// @ts-check
const { test, expect } = require('@playwright/test');

test('login form', async ({ page }) => {
  await page.goto('http://localhost:3000/login');

  const form = page.getByTestId('login-form');

  expect(form).toBeDefined();
});

test('login with correct email and password', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  
  // Fill out the form
  const email = process.env.TEST_LOGIN_EMAIL ? process.env.TEST_LOGIN_EMAIL : '';
  const password = process.env.TEST_LOGIN_PASSWORD ? process.env.TEST_LOGIN_PASSWORD : '';
  await page.getByLabel('email').fill(email);
  await page.getByLabel('password').fill(password);

  //  Submit the form
  await page.getByRole('button', {name: /login/i}).click();

  // Expects the URL to contain intro.
  await expect(page).toHaveURL(/.*dashboard/);
});

test('login with wrong password', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  
  // Fill out the form
  const email = process.env.TEST_LOGIN_EMAIL ? process.env.TEST_LOGIN_EMAIL : '';
  await page.getByLabel('email').fill(email);
  await page.getByLabel('password').fill('wrongpassword');

  //  Submit the form
  await page.getByRole('button', {name: /login/i}).click();

  // Expects the URL to contain intro.
  await expect(page).toHaveURL(/.*login/);
});
