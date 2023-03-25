// scroll bar
import 'simplebar/src/simplebar.css';

import ReactDOM from 'react-dom';
import { BrowserRouter } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { Auth0Provider } from "@auth0/auth0-react";


// ** Redux Imports
import { Provider } from 'react-redux';
import store from './redux/store';

//
import App from './App';
import * as serviceWorker from './serviceWorker';
import reportWebVitals from './reportWebVitals';
import 'font-awesome/css/font-awesome.min.css'; // font-awesome



// ----------------------------------------------------------------------

ReactDOM.render(
  <Auth0Provider
    domain="dev-xv7akt6j0j1ojdng.us.auth0.com"
    clientId="f2pIlCewKkwJm70CE7IWXPOpOgkijCym"
    authorizationParams={{
      redirect_uri: "http://localhost:3000/dashboard/customers"
    }}
  >
    <HelmetProvider>
      <BrowserRouter>
        <Provider store={store}>
          <App />
        </Provider>
      </BrowserRouter>
    </HelmetProvider>
  </Auth0Provider>,
  document.getElementById('root')
);

// If you want to enable client cache, register instead.
serviceWorker.unregister();

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
