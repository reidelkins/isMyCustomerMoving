// scroll bar
import 'simplebar/src/simplebar.css';

import ReactDOM from 'react-dom';
import { BrowserRouter } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { GoogleOAuthProvider } from '@react-oauth/google';



// ** Redux Imports
import { Provider } from 'react-redux';
import store from './redux/store';

//
import App from './App';
import * as serviceWorker from './serviceWorker';
import reportWebVitals from './reportWebVitals';
import 'font-awesome/css/font-awesome.min.css'; // font-awesome

const { REACT_APP_GOOGLE_CLIENT_ID } = process.env



// ----------------------------------------------------------------------

ReactDOM.render(
  
  <HelmetProvider>
    <BrowserRouter>
        <GoogleOAuthProvider clientId={REACT_APP_GOOGLE_CLIENT_ID}>
          <Provider store={store}>
            <App />
          </Provider>
        </GoogleOAuthProvider>
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
