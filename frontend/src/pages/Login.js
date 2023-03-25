import React from 'react';
import { useAuth0 } from "@auth0/auth0-react";

// components
import Page from '../components/Page';
import { PageLoader } from '../components/PageLoader';


// ----------------------------------------------------------------------

// ----------------------------------------------------------------------

export default function Login() {
  const { loginWithRedirect } = useAuth0();
  loginWithRedirect();
  return (
    <Page title="Login | isMyCustomerMoving">
      <PageLoader />
    </Page>
  );
};


  
