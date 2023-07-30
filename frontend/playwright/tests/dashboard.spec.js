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
        await responsePromise;
    });

    test('table defaults to 10 rows', async ({ page }) => {
        const table = page.getByTestId('customer-data-table');

        const rows = await table.locator('tbody tr').count()
        expect(rows).toBe(10);
    });

    test('change from 10 to 50 clients per page', async ({ page }) => {        
        await page.getByRole('button', { name: '10' }).click();
        
        const dropDown = page.getByRole('listbox');
        expect(dropDown).toBeVisible();
    });


 })