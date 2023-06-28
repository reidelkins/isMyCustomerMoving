const { REACT_APP_ENVIRONMENT } = process.env;

const DOMAIN =
  REACT_APP_ENVIRONMENT === 'dev' ? 'http://localhost:8000' : 'https://is-my-customer-moving.herokuapp.com';
const URL = REACT_APP_ENVIRONMENT === 'dev' ? 'http://localhost:3000' : 'https://app.ismycustomermoving.com';

export { DOMAIN, URL };
