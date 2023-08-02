// @ts-check
const { test, expect } = require('@playwright/test');
import { generateRandomString } from './helpers';

const NON_ADMIN_USER = 'testuser2@test.com';
const NEW_USER_EMAIL = 'newuser@test.com';
const PENDING_USER_EMAIL = 'testuser3@test.com';
const USER_TO_BE_DELETED = 'deleteme@test.com';

test.describe('edit profile info', () => {
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

test.describe('create user and send email', () => {
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
  });

  test('send reminder email', async ({ page }) => {
    const responsePromise = page.waitForResponse('**/api/v1/accounts/manageuser/**');
    const newUserRow = page.locator(`tr:has-text("${PENDING_USER_EMAIL}")`);
    await newUserRow.getByRole('button', { name: /send reminder/i }).click();

    const response = await responsePromise;
    expect(response.status()).toBe(200);
  });
});

test.describe('make user admin and delete user', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard/settings/user');
    await createUser(page, USER_TO_BE_DELETED);
  });

//   test('make normal user an admin', async ({ page }) => {
//     const responsePromise = page.waitForResponse('**/api/v1/accounts/manageuser/**');
//     const row = page.locator(`tr:has-text("${NON_ADMIN_USER}")`);
//     await row.getByRole('button', { name: /make admin/i }).click();

//     const response = await responsePromise;
//     expect(response.status()).toBe(200);

//     // delete user
//     await deleteUser(page, NON_ADMIN_USER);
//   });

  test('delete user', async ({ page }) => {
    const responsePromise = page.waitForResponse('**/api/v1/accounts/manageuser/**');
    const targetUserROw = page.locator(`tr:has-text("${USER_TO_BE_DELETED}")`);
    await targetUserROw.getByRole('checkbox').check();

    await page.getByLabel('Delete').click();

    const response = await responsePromise;
    expect(response.status()).toBe(200);
  });
});

async function createUser(page, email) {
  await page.goto('/dashboard/settings/user');
  const targetUserROw = page.locator(`tr:has-text("${USER_TO_BE_DELETED}")`);

  // create user if it doesn't exist
  if (!(await targetUserROw.isVisible())) {
    const responsePromise = page.waitForResponse('**/api/v1/accounts/manageuser/**');

    await page.getByLabel('Add User').click();
    const addUserModal = page.getByTestId('add-user-modal');
    await expect(addUserModal).toBeVisible();

    await addUserModal.getByRole('textbox').fill(email);
    await addUserModal.getByText('Submit').click();

    await responsePromise;
  } else {
    console.log(`User ${email} already exists`);
  }
}

async function deleteUser(page, email) {
  await page.goto('/dashboard/settings/user');
  const targetUserROw = page.locator(`tr:has-text("${USER_TO_BE_DELETED}")`);

  // delete user if it exists
  if (await targetUserROw.isVisible()) {
    const table = page.getByTestId('users-table');
    const row = table.locator(`tr:has-text("${email}")`);
    await row.getByRole('checkbox').check();

    await page.getByLabel('Delete').click();
  } else {
    console.log(`User ${email} does not exist`);
  }
}


