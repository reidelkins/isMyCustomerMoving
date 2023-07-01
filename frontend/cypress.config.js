const { defineConfig } = require('cypress');

// load the environment variables from the local .env file
require('dotenv').config()

module.exports = defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      // implement node event listeners here
      // we can grab some process environment variables
      // and stick it into config.env before returning the updated config
      config.env = config.env || {};

      config.env.LOGIN_EMAIL = process.env.CYPRESS_LOGIN_EMAIL;
      config.env.LOGIN_PASSWORD = process.env.CYPRESS_LOGIN_PASSWORD;

      return config;
    },
  },
});
