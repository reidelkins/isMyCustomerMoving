// @ts-check
import { test, expect } from '@playwright/test';
import { ZIP_CODE, CITY, STATE } from '../utils/constants';

test.describe('pagination', () => {
  test.beforeEach(async ({ page }) => {
    await setupForSalePage(page);
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
    // Click pagination and change to 50 rows
    await page.getByLabel('10').click();
    await page.getByRole('option', { name: '100' }).click();

    await expect(page.getByLabel('100')).toBeVisible();
  });
});

test.describe('filter', () => {
  test.beforeEach(async ({ page }) => {
    await setupForSalePage(page);
  });

  test('by zip code', async ({ page }) => {
    const filterResponsePromise = page.waitForResponse(
      `**/api/v1/data/forsale/?page=1&tags=&zip_code=${ZIP_CODE}`
    );
    await page.getByLabel('Filter list').click();
    await page.getByLabel('This will filter for the city state and zip of the home').getByRole('spinbutton').click();
    await page
      .getByLabel('This will filter for the city state and zip of the home')
      .getByRole('spinbutton')
      .fill(ZIP_CODE);
    await page
      .getByLabel('This will filter for the city state and zip of the home')
      .getByRole('spinbutton')
      .press('Enter');

    const response = await filterResponsePromise;
    expect(response.status()).toBe(200);
  });

  test('by city', async ({ page }) => {
    const filterResponsePromise = page.waitForResponse(`**/api/v1/data/forsale/?page=1&tags=&city=${CITY}`);
    await page.getByLabel('Filter list').click();
    await page
      .locator('div')
      .filter({ hasText: /^City$/ })
      .getByRole('textbox')
      .click();
    await page
      .locator('div')
      .filter({ hasText: /^City$/ })
      .getByRole('textbox')
      .fill(CITY);
    await page.getByRole('button', { name: 'Apply Filters' }).click();

    const response = await filterResponsePromise;
    expect(response.status()).toBe(200);
  });

  test('by state', async ({ page }) => {
    const filterResponsePromise = page.waitForResponse(`**/api/v1/data/forsale/?page=1&tags=&state=${STATE}`);
    await page.getByLabel('Filter list').click();
    await page
      .locator('div')
      .filter({ hasText: /^State$/ })
      .getByRole('textbox')
      .click();
    await page
      .locator('div')
      .filter({ hasText: /^State$/ })
      .getByRole('textbox')
      .fill(STATE);
    await page.getByRole('button', { name: 'Apply Filters' }).click();

    const response = await filterResponsePromise;
    expect(response.status()).toBe(200);
  });
});

const setupForSalePage = async (page) => {
  const responsePromise = page.waitForResponse('**/api/v1/data/forsale/?page=1');

  await page.goto('/dashboard/forsale');
  await page.waitForLoadState('load');

  // Wait for the first page of clients from the API
  const response = await responsePromise;
  expect(response.status()).toBe(200);
};
