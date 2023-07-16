// @ts-check
const { test, expect } = require('@playwright/test');


test.describe('Editing profile info', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/dashboard/settings/user');
        await page.getByTestId('edit-profile').click();
    });
    
    test('change name and phone number', async ({ page }) => {
        const responsePromise = page.waitForResponse('**/api/v1/accounts/manageuser/**');
        const newFirstName = generateRandomString(5);
        const newLastName = generateRandomString(5);
        const newPhoneNumber = generateRandomString(10);

        await page.getByLabel('First Name').fill(newFirstName);
        await page.getByLabel('Last Name').fill(newLastName);
        await page.getByLabel('Phone').fill(newPhoneNumber);
        await page.getByTestId('update-profile-button').click();

        const response = await responsePromise;
        expect(response.status()).toBe(200);

        const profileData = page.getByTestId('profile-data');
        await expect(profileData).toHaveText(new RegExp(newFirstName, 'g'));
        await expect(profileData).toHaveText(new RegExp(newLastName, 'g'));
        await expect(profileData).toHaveText(new RegExp(newPhoneNumber, 'g'));
    });
});

function generateRandomString(length) {
    let result = '';
    let characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let charactersLength = characters.length;
    for (let i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
}