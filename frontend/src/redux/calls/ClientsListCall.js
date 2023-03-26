import { useEffect, useState, memo } from 'react';

import { useDispatch } from 'react-redux';
import { useAuth0 } from "@auth0/auth0-react";

import { clientsAsync } from '../actions/usersActions';
// import { useAccessToken } from '../../utils/getAccessToken';


const ClientsListCall = () => {
  // ** Store Vars
  const dispatch = useDispatch();
  const { getAccessTokenSilently } = useAuth0();
  const [accessToken, setAccessToken] = useState(null);

  useEffect(() => {
    const fetchAccessToken = async () => {
      const token = await getAccessTokenSilently();
      setAccessToken(token);
    };

    fetchAccessToken();

    // return a cleanup function to cancel any pending async operation and prevent updating the state on an unmounted component
    return () => {
      setAccessToken(null);
    };
  }, [getAccessTokenSilently]);


  // ** Get data on mount
  useEffect(() => {
    if (accessToken) {
      dispatch(clientsAsync(1, accessToken));
    }
  }, [dispatch, accessToken]);

  return null;
};

export default memo(ClientsListCall);
