// @ts-check
const { test, expect } = require('@playwright/test');
import { delay, generateRandomString, getFinalCounterNumber } from './helpers';

test.describe('pagination', () => {
  test.beforeEach(async ({ page }) => {
    await setupCustomerDashboard(page);
  });

  test('default show 10 clients', async ({ page }) => {
    const rows = page.locator('tr');
    expect(await rows.count()).toBe(11);
  });

  test('show 50 clients', async ({ page }) => {
    const rows = page.locator('tr');

    // Click pagination and change to 50 rows
    await page.getByLabel('10').click();
    await page.getByRole('option', { name: '50' }).click();

    expect(await rows.count()).toBe(51);
  });

  test('show 100 clients', async ({ page }) => {
    const rows = page.locator('tr');

    // Click pagination and change to 50 rows
    await page.getByLabel('10').click();
    await page.getByRole('option', { name: '100' }).click();

    expect(await rows.count()).toBe(101);
  });
});

test.describe('contact for sale customers', () => {
  test.beforeEach(async ({ page }) => {
    await setupCustomerDashboard(page);
  });

  test('click contacted', async ({ page }) => {
    const responsePromise = page.waitForResponse('**/api/v1/data/updateclient/');
    const firstContactButton = page.locator('tr').getByLabel('Not Contacted').first();
    await firstContactButton.click();
    const response = await responsePromise;
    expect(response.status()).toBe(201);
    // TODO - figure out how to verify check mark is visible
  });

  test('un-click contacted', async ({ page }) => {
    const responsePromise = page.waitForResponse('**/api/v1/data/updateclient/');
    const firstContactedButton = page.locator('tr').getByLabel('Contacted').first();
    await firstContactedButton.click();
    const response = await responsePromise;
    expect(response.status()).toBe(201);
  });

  test('for sale number decreases', async ({ page }) => {
    const oldForSaleNumber = await getFinalCounterNumber(page, 'For Sale');

    // Contact a for sale customer
    const firstNotContactedHouseForSale = page
      .locator('tr')
      .filter({ hasText: 'House for sale' })
      .getByLabel('Not Contacted')
      .first();
    await firstNotContactedHouseForSale.click();

    const newForSaleNumber = await getFinalCounterNumber(page, 'For Sale');
    expect(newForSaleNumber).toEqual(oldForSaleNumber - 1);
  });

  test('for sale number increases', async ({ page }) => {
    const oldForSaleNumber = await getFinalCounterNumber(page, 'For Sale');

    // (Un)contact a for sale customer
    const firstNotContactedHouseForSale = page
      .locator('tr')
      .filter({ hasText: 'House for sale' })
      .getByLabel('Contacted')
      .first();
    await firstNotContactedHouseForSale.click();

    const newForSaleNumber = await getFinalCounterNumber(page, 'For Sale');
    expect(newForSaleNumber).toEqual(oldForSaleNumber + 1);
  });
});

test.describe('contact recently sold customers', () => {
  test.beforeEach(async ({ page }) => {
    await setupCustomerDashboard(page);
  });

  test('contact', async ({ page }) => {
    const responsePromise = page.waitForResponse('**/api/v1/data/updateclient/');
    const oldRecentlySoldNumber = await getFinalCounterNumber(page, 'Recently Sold');

    // Filter for recently sold and contact the first customer
    await page.getByLabel('Filter list').click();
    await page.getByLabel('Recently Sold').check();
    await page.getByRole('button', { name: 'Apply Filters' }).click();
    await page.locator('tr').filter({ hasText: 'recently sold' }).getByLabel('Not Contacted').first().click();
    const response = await responsePromise;

    //  Assert API request successful and counter decremented
    expect(response.status()).toBe(201);
    const newRecentlySoldNumber = await getFinalCounterNumber(page, 'Recently Sold');
    expect(newRecentlySoldNumber).toEqual(oldRecentlySoldNumber - 1);
  });

  test('uncontact', async ({ page }) => {
    const responsePromise = page.waitForResponse('**/api/v1/data/updateclient/');
    const oldRecentlySoldNumber = await getFinalCounterNumber(page, 'Recently Sold');

    // Filter for recently sold and contact the first customer
    await page.getByLabel('Filter list').click();
    await page.getByLabel('Recently Sold').check();
    await page.getByRole('button', { name: 'Apply Filters' }).click();
    await page.locator('tr').filter({ hasText: 'recently sold' }).getByLabel('Contacted').first().click();
    const response = await responsePromise;

    //  Assert API request successful and counter decremented
    expect(response.status()).toBe(201);
    const newRecentlySoldNumber = await getFinalCounterNumber(page, 'Recently Sold');
    expect(newRecentlySoldNumber).toEqual(oldRecentlySoldNumber + 1);
  });
});

test.describe('delete clients', () => {
  test.beforeEach(async ({ page }) => {
    await setupCustomerDashboard(page);
  });
  
  // test('first customer', async ({ page }) => {
  //   await page.locator('tr').getByRole('checkbox').first().check();
  //   await page.getByLabel('Delete').first().click();
  //   // TODO - assert something
  // })
})

test.describe('make note', () => {
  test.beforeEach(async ({ page }) => {
    await setupCustomerDashboard(page);
  });

  test('random string', async ({ page }) => {
    const note = generateRandomString(6);
    const responsePromise = page.waitForResponse('**/api/v1/data/updateclient/');

    await page.getByLabel('View/Edit Note').first().click();
    const noteForm = page.getByTestId('note-form');
    await noteForm.getByRole('textbox').fill(note);
    await page.getByRole('button', { name: 'Submit' }).click();

    const response = await responsePromise;
    expect(response.status()).toBe(201);

    await page.reload();

    // Click note and verify it has text "this is a note"
    await page.getByLabel('View/Edit Note').first().click();
    await expect(noteForm).toHaveText(new RegExp(note, 'g'));
  });
});

const setupCustomerDashboard = async (page) => {
  await page.goto('/dashboard/customers');
  await page.waitForLoadState('load');

  // Wait for the first page of clients from the API
  const responsePromise = page.waitForResponse('**/api/v1/data/clients/?page=1');
  const response = await responsePromise;
  expect(response.status()).toBe(200);
};
