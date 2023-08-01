// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Pagination', () => {
  test.beforeEach(async ({ page }) => {
    // Add listeners for request and response events
    // page.on('request', (request) => {console.log('>>', request.method(), request.url())});
    // page.on('response', (response) => {console.log('<<', response.status(), response.url())});

    await page.goto('/dashboard/customers');
    await page.waitForLoadState('load');

    // Wait for the first page of clients from the API
    const responsePromise = page.waitForResponse('**/api/v1/data/clients/?page=1');
    const response = await responsePromise;
    expect(response.status()).toBe(200);
  });

  test('default show 10 clients', async ({ page }) => {
    const rows = page.locator('tr');
    expect(await rows.count()).toBe(11);
  });

  test('show 50 clients', async ({ page }) => {
    const rows = page.locator('tr');

    // Click pagination and change to 50 rows
    await page.getByLabel('10').click()
    await page.getByRole('option', { name: '50' }).click()

    expect(await rows.count()).toBe(51);
  });

  test('show 100 clients', async ({page}) => {
    const rows = page.locator('tr');

    // Click pagination and change to 50 rows
    await page.getByLabel('10').click()
    await page.getByRole('option', { name: '100' }).click()

    expect(await rows.count()).toBe(101);
  })
});
