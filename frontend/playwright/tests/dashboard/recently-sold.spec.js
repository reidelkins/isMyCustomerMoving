const { test, expect } = require('@playwright/test');

test.describe('pagination', () => {
  test.beforeEach(async ({ page }) => {
    await setupRecentlySoldPage(page);
  });

  test('download button exists', async ({ page }) => {
    const downloadButton = page.getByRole('link', { name: 'Download To CSV' });
    await expect(downloadButton).toBeVisible();
  })

//   test('default show 10 clients', async ({ page }) => {
//     const rows = page.locator('tr');
//     expect(await rows.count()).toBe(11);
//   });

//   test('show 50 clients', async ({ page }) => {
//     const rows = page.locator('tr');

//     // Click pagination and change to 50 rows
//     await page.getByLabel('10').click();
//     await page.getByRole('option', { name: '50' }).click();

//     expect(await rows.count()).toBe(51);
//   });

//   test('show 100 clients', async ({ page }) => {
//     const rows = page.locator('tr');

//     // Click pagination and change to 50 rows
//     await page.getByLabel('10').click();
//     await page.getByRole('option', { name: '100' }).click();

//     expect(await rows.count()).toBe(101);
//   });
});

const setupRecentlySoldPage = async (page) => {
    await page.goto('/dashboard/recentlysold');
    await page.waitForLoadState('load');
  
    // Wait for the first page of clients from the API
    const responsePromise = page.waitForResponse('**/api/v1/data/recentlysold/?page=1');
    const response = await responsePromise;
    expect(response.status()).toBe(200);
  };