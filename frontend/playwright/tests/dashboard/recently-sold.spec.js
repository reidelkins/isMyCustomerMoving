const { test, expect } = require('@playwright/test');

test.describe('pagination', () => {
  test.beforeEach(async ({ page }) => {
    await setupRecentlySoldPage(page);
  });

  test('default show 10 clients', async ({ page }) => {
    await expect(page.getByLabel('10')).toBeVisible();
  });

  test('show 50 clients', async ({ page }) => {
    // Click pagination and change to 50 rows
    await page.getByLabel('10').click();
    await page.getByRole('option', { name: '50' }).click();

    await expect(page.getByLabel('50')).toBeVisible();
  });

  test('show 100 clients', async ({ page }) => {
    await page.getByLabel('10').click();
    await page.getByRole('option', { name: '100' }).click();

    await expect(page.getByLabel('100')).toBeVisible();
  });
});

const setupRecentlySoldPage = async (page) => {
    const responsePromise = page.waitForResponse('**/api/v1/data/recentlysold/?page=1');
    
    await page.goto('/dashboard/recentlysold');
    await page.waitForLoadState('load');
  
    // Wait for the first page of clients from the API
    const response = await responsePromise;
    expect(response.status()).toBe(200);
  };