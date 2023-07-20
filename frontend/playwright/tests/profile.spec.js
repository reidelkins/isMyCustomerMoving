// @ts-check
const { test, expect } = require('@playwright/test');

const NON_ADMIN_USER = 'testuser2@gmail.com'
const NEW_USER_EMAIL = 'newuser@gmail.com'
const PENDING_USER_EMAIL = 'testuser3@gmail.com'
const USER_TO_BE_DELETED = 'deleteme@test.com'


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

test.describe('Create new user', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/dashboard/settings/user');
    });

    test('create user', async ({ page }) => {
        const responsePromise = page.waitForResponse('**/api/v1/accounts/manageuser/**');

        await page.getByLabel('Add User').click();
        const addUserModal = page.getByTestId('add-user-modal');
        await expect(addUserModal).toBeVisible();

        const newUserEmail = NEW_USER_EMAIL;
        
        await addUserModal.getByRole('textbox').fill(newUserEmail);
        await addUserModal.getByText('Submit').click();

        const response = await responsePromise;
        expect(response.status()).toBe(200);
        // TODO - make this more precise.  If random email is repeated, this test will pass when it shouldn't
        const table = page.getByTestId('users-table');
        await expect(table).toHaveText(new RegExp(newUserEmail, 'g'));
        await expect(addUserModal).not.toBeVisible();
    });

    test('fail to create user with invalid email', async ({ page }) => {
        await page.getByLabel('Add User').click();
        const addUserModal = page.getByTestId('add-user-modal');
        await expect(addUserModal).toBeVisible();

        await addUserModal.getByRole('textbox').fill('invalidemail');
        await addUserModal.getByText('Submit').click();

        await expect(addUserModal).toBeVisible();
        await expect(addUserModal).toHaveText(/Email must be a valid email address/);
    })

    test('send reminder email', async ({ page }) => {
        const responsePromise = page.waitForResponse('**/api/v1/accounts/manageuser/**');
        const newUserRow = page.locator(`tr:has-text("${PENDING_USER_EMAIL}")`);
        await newUserRow.getByRole('button', {name: /send reminder/i}).click();

        const response = await responsePromise;
        expect(response.status()).toBe(200);
    });

    test('make normal user an admin', async ({ page }) => {
        const responsePromise = page.waitForResponse('**/api/v1/accounts/manageuser/**');
        const row = page.locator(`tr:has-text("${NON_ADMIN_USER}")`);
        await row.getByRole('button', {name: /make admin/i}).click();

        const response = await responsePromise;
        expect(response.status()).toBe(200);
    });

    test('delete new user', async ({ page }) => {
        const responsePromise = page.waitForResponse('**/api/v1/accounts/manageuser/**');
        const newUserRow = page.locator(`tr:has-text("${USER_TO_BE_DELETED}")`);
        await newUserRow.getByRole('checkbox').check();

        await page.getByLabel('Delete').click();

        const response = await responsePromise;
        expect(response.status()).toBe(200);
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