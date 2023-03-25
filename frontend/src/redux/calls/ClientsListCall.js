import { useEffect, memo } from 'react';

import { useDispatch } from 'react-redux';
import { useAuth0 } from "@auth0/auth0-react";

import { clientsAsync } from '../actions/usersActions';

const ClientsListCall = () => {
  // ** Store Vars
  const dispatch = useDispatch();

  const { getAccessTokenSilently } = useAuth0();

  // ** Get data on mount
  useEffect(async () => {
    const accessToken = await getAccessTokenSilently();
    dispatch(clientsAsync(accessToken, 1));
    console.log("Doing This Now")
  }, [dispatch]);

  return null;
};

export default memo(ClientsListCall);
