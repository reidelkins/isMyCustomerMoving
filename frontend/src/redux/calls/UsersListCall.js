import { useEffect, useState, memo } from 'react';

import { useDispatch } from 'react-redux';
import { useAuth0 } from "@auth0/auth0-react";

import { usersAsync } from '../actions/usersActions';

const UsersListCall = () => {
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
      dispatch(usersAsync(accessToken));
    }
  }, [dispatch, accessToken]);

  return null;
};

export default memo(UsersListCall);
