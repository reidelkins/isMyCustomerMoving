// scroll bar
import 'simplebar/dist/simplebar.css';

import ReactDOM from 'react-dom';
import { BrowserRouter } from 'react-router-dom';
import { HelmetProvider, Helmet } from 'react-helmet-async';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { RowndProvider } from '@rownd/react';
// ** Redux Imports
import { Provider } from 'react-redux';
import store from './redux/store';

//
import App from './App';
import * as serviceWorker from './serviceWorker';
import reportWebVitals from './reportWebVitals';
import 'font-awesome/css/font-awesome.min.css'; // font-awesome

const { REACT_APP_GOOGLE_CLIENT_ID, REACT_APP_ROWND_APP_KEY } = process.env;

// ----------------------------------------------------------------------

ReactDOM.render(
  <HelmetProvider>
    <Helmet>
      <title>Is My Customer Moving</title>
      <meta name="description" content="Is My Customer Moving" />
      <script
        // eslint-disable-next-line react/no-danger
        dangerouslySetInnerHTML={{
          __html: `(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
      new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
      j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
      'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
      })(window,document,'script','dataLayer','GTM-N6RJ2R7');`,
        }}
      />
    </Helmet>
    <noscript
      // eslint-disable-next-line react/no-danger
      dangerouslySetInnerHTML={{
        __html: `<iframe src="https://www.googletagmanager.com/ns.html?id=GTM-N6RJ2R7"
      height="0" width="0" style="display:none;visibility:hidden"></iframe>`,
      }}
    />
    <RowndProvider
      appKey={REACT_APP_ROWND_APP_KEY}
      postLoginRedirect="/dashboard"
    >
      <BrowserRouter>
        <GoogleOAuthProvider clientId={REACT_APP_GOOGLE_CLIENT_ID}>
          <Provider store={store}>
            <App />
          </Provider>
        </GoogleOAuthProvider>
      </BrowserRouter>
    </RowndProvider>
  </HelmetProvider>,
  document.getElementById('root')
);

// If you want to enable client cache, register instead.
serviceWorker.unregister();

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
