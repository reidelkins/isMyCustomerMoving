// scroll bar
import 'simplebar/src/simplebar.css';

import ReactDOM from 'react-dom';
import { BrowserRouter } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';



// ** Redux Imports
import { Provider } from 'react-redux';
import store from './redux/store';

//
import App from './App';
import { Auth0ProviderWithNavigate } from './auth0ProviderWithNavigate';
import * as serviceWorker from './serviceWorker';
import reportWebVitals from './reportWebVitals';
import 'font-awesome/css/font-awesome.min.css'; // font-awesome



// ----------------------------------------------------------------------

ReactDOM.render(
  
  <HelmetProvider>
    <BrowserRouter>
      <Auth0ProviderWithNavigate>
        <Provider store={store}>
          <App />
        </Provider>
      </Auth0ProviderWithNavigate>
    </BrowserRouter>
  </HelmetProvider>,
  document.getElementById('root')
);

// If you want to enable client cache, register instead.
serviceWorker.unregister();

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
