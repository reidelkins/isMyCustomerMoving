// @ts-check
const { test, expect } = require('@playwright/test');


test.describe('Interacting with client data', () => { 
    test.beforeEach(async ({ page }) => {
        await page.goto('/dashboard/customers');
    });

    // test('pagination', async ({ page }) => {
    //     const container = page.getByTestId('customer-data-card');
    //     expect(container).toBeVisible();
    // });


 })