Frontend Tests 28 June 2023

## End to End tests
 
 This CRA (create-react-app) uses Playwright for end-to-end testing.  Below is the end-to-end test plan.

#### Auth

- [x] Auth
  - [x] Log in correct email + password
  - [x] Fail login w/incorrect password 
- [x] Log out
- [ ] Log in using google SSO (not working)

#### Routes
- [x] /dashboard
- [x] /dashboard/customers
- [x] /dashboard/referrals
- [x] /dashboard/forsale
- [x] /dashboard/recentlysold
- [x] /dashboard/settings/user
- [x] /dashboard/settings/enterprise
- [x] Protected routes (ensure these require auth)

#### Profile Settings

- [x] Edit first name
- [x] Edit last name
- [ ] Edit email
- [x] Edit phone number
- [x] Add User
  - [x] Email input validation
  - [x] Send Reminder Email
  - [x] Make User Admin
  - [x] Delete user

*gonna need your help here*
**REID: You can use fake numbers for all of this, nothing here is actually testing a connection**
- [x] Connect To Service Titan
  - [x] Add Tenant ID
  - [x] Then should see button to add client ID and secret
    - [x] Add client ID and secret
  - [x] Then should be able to add tag IDs
    - [x] Add tag IDs
  - [x] Then should be able to EDIT tag IDs

#### Customer Data

- [x] Show 10 per page, 50, 100 clients
- [ ] View more than 1000 clients  *this test would take 2+ mins*
**how should I test this?  Just click through pages?** 
**REID: YES**
- [x] Make note
- [x] Set as contacted/not contacted
  - [x] For sale number increments
  - [x] For sale number decrements
  - [x] Recently sold increments
  - [x] Recently sold decrements
  - [x] Make sure cannot see contacted checkbox if status is “No Change”
- [x] Delete a client
- [x] Delete multiple clients
- [x] Search by name
- [x] Search by address
- [x] View map
- [x] Filter by
  - [x] For Sale
  - [x] Recently Sold
  - [x] Off Market (No Change)
  - [ ] Zip
  - [ ] City
  - [ ] State
  - [ ] Min/max price
  - [ ] Min/max housing built year
  - [ ] Min/max customer since date
  - [ ] Tags
  - [ ] Equipment Install Date (Not Tested Yet)
- [ ] Download all to CSV *hard to verify the download*
  - [ ] Download all
  - [ ] Download filtered list
- [ ] Upload Clients with File (Not Tested Yet)
- [ ] Sync Clients with service titan (Must have added service titan integration in order to see this)
- [ ] Check for all three options

#### Recently sold data and for sale
- [x] Show 10 per page, 50, 100
- [ ] View more than 1000 clients *same problem here*
- [ ] Download (TODO: not currently auto filtering for less than 30 days)
  - [ ] All
  - [ ] Filtered
- [ ] Filter by
  - [ ] Saved Filter
  - [ ] Zip
  - [ ] City
  - [ ] State
  - [ ] Min/Max Housing Price
  - [ ] Min/Max year built
  - [ ] Tags
  - [ ] Min/Max days ago
- [ ] Save Filter
  - [ ] Create a new filter, with and without zapier
  - [ ] Test the new filter
- [ ] All Two Factor Auth (no one uses this, has not been manually tested)
- [ ] Active vs admin user
  - [ ] Can only see clients with status
  - [ ] Can not download anything
  - [ ] Can not upload anything
  - [ ] Can not add users, delete users, or change status of users
- [ ] Free tier vs not free tier shows pop up’s and alerts as expected
