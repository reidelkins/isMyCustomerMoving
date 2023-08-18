// @ts-check
import { test, expect } from '@playwright/test';
import { generateRandomString, getFinalCounterNumber } from '../utils/helpers';

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
    // await page.getByLabel('Filter list').click();
    // await page.getByLabel('Recently Sold').check();
    // await page.getByRole('button', { name: 'Apply Filters' }).click();
    // await page.locator('tr').filter({ hasText: 'recently sold' }).getByLabel('Not Contacted').first().click();

    // (Un)contact a for sale customer
    const firstNotContactedRecentlySoldClient = page
      .locator('tr')
      .filter({ hasText: 'recently sold' })
      .getByLabel('Not Contacted')
      .first();
    await firstNotContactedRecentlySoldClient.click();
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
    // await page.getByLabel('Filter list').click();
    // await page.getByLabel('Recently Sold').check();
    // await page.getByRole('button', { name: 'Apply Filters' }).click();
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

  test('delete Bruce Wayne', async ({ page }) => {
    await page
      .locator('tr')
      .filter({ hasText: 'Bruce Wayne1007 Mountain DriveGotham CityNY37919House for sale(414) 326-8313' })
      .getByRole('checkbox')
      .check();
    await page.getByLabel('Delete').click();
    await expect(
      page
        .locator('tr')
        .filter({ hasText: 'Bruce Wayne1007 Mountain DriveGotham CityNY37919House for sale(414) 326-8313' })
    ).toHaveCount(0);
  });

  test('delete both Gordons', async ({ page }) => {
    await page
      .locator('tr')
      .filter({ hasText: 'Barbara Gordon500 Oracle StGotham CityNY37919House for sale(414) 326-8315' })
      .getByRole('checkbox')
      .check();
    await page
      .locator('tr')
      .filter({ hasText: 'Jim Gordon1 Police PlazaGotham CityNY37919House for sale(414) 326-8316' })
      .getByRole('checkbox')
      .check();
    await page.getByLabel('Delete').click();
    await expect(
      page
        .locator('tr')
        .filter({ hasText: 'Barbara Gordon500 Oracle StGotham CityNY37919House for sale(414) 326-8315' })
    ).toHaveCount(0);
    await expect(
      page.locator('tr').filter({ hasText: 'Jim Gordon1 Police PlazaGotham CityNY37919House for sale(414) 326-8316' })
    ).toHaveCount(0);
  });
});

test.describe('search and view map', () => {
  test.beforeEach(async ({ page }) => {
    await setupCustomerDashboard(page);
  });

  test('search for Harvey Dent by name', async ({ page }) => {
    await page.getByPlaceholder('Search user...').click();
    await page.getByPlaceholder('Search user...').fill('Harvey Dent');
    await page.getByPlaceholder('Search user...').press('Enter');
    
    const results = page.getByLabel('Click For Expanded Details')
    await expect(results).toHaveText(/Harvey Dent/);
  });

  test('search for Selina Kyle by address', async ({ page }) => {
    await page.getByPlaceholder('Search user...').click();
    await page.getByPlaceholder('Search user...').fill('69 Meow St');
    await page.getByPlaceholder('Search user...').press('Enter');

    const results = page.getByLabel('Click For Expanded Details')
    await expect(results).toHaveText(/Selina Kyle/);
  })

  test('view map', async ({ page}) => {
    await page.getByRole('button', { name: 'Map' }).click();
    const map = page.locator('div').filter({ hasText: /^To navigate, press the arrow keys\.$/ }).first()
    await expect(map).toBeVisible();
  })  
});

test.describe('filter table', () => {
  test.beforeEach(async ({ page }) => {
    await setupCustomerDashboard(page);
  });

  test('for sale',async ({ page }) => {
    const filterRequestPromise = page.waitForResponse('**/api/v1/data/clients/?page=1&status=For%20Sale');
    await page.getByLabel('Filter list').click();
    await page.getByLabel('For Sale').check();
    await page.getByRole('button', { name: 'Apply Filters' }).click();

    const response = await filterRequestPromise;
    expect(response.status()).toBe(200);

    const firstRow = page.getByLabel('Click For Expanded Details').first();
    await expect(firstRow).toHaveText(/for sale/);
  })

  test('recently sold',async ({ page }) => {
    const filterRequestPromise = page.waitForResponse('**/api/v1/data/clients/?page=1&status=Recently%20Sold');
    await page.getByLabel('Filter list').click();
    await page.getByLabel('Recently Sold').check();
    await page.getByRole('button', { name: 'Apply Filters' }).click();
    
    const response = await filterRequestPromise;
    expect(response.status()).toBe(200);

    const firstRow = page.getByLabel('Click For Expanded Details').first();
    await expect(firstRow).toHaveText(/recently sold/);
  })});

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
  const responsePromise = page.waitForResponse('**/api/v1/data/clients/?page=1');
  await page.goto('/dashboard/customers');
  await page.waitForLoadState('load');

  // Wait for the first page of clients from the API
  const response = await responsePromise;
  expect(response.status()).toBe(200);
};
