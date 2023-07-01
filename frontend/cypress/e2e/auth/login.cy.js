const EMAIL = Cypress.env('LOGIN_EMAIL')
const PASSWORD = Cypress.env('LOGIN_PASSWORD')
// const EMAIL = "jack.richard.long@gmail.com"
// const PASSWORD = "password"

describe('login at /login', () => { 
    beforeEach(() => {
        cy.visit('http://localhost:3000/login')
    })
    it('email and password env variables should be set', () => {
        expect(EMAIL).to.not.be.empty
        expect(PASSWORD).to.not.be.empty
    })
    it('should display login page', () => {
        cy.get("[data-cy=login-form]").should('be.visible')
    })
    it('login', () => {
        // Fill out the form
        cy.get('input[name=email]').type(EMAIL)
        cy.get('input[name=password]').type(PASSWORD)

        // Submit the form
        cy.get("[data-cy=login-form]").submit()

        // Check the resulting page
        cy.url().should('include', '/dashboard')
        cy.get('h4').should('contain', 'Welcome')
    })
    it('login with wrong password', () => {
        // Fill out the form
        cy.get('input[name=email]').type(EMAIL)
        cy.get('input[name=password]').type('wrongpassword')

        cy.get("[data-cy=login-form]").submit()

        // Check the resulting page
        cy.url().should('include', '/login')
        cy.get("[data-cy=login-alert]").should('contain', 'Login Error')
    })


 })