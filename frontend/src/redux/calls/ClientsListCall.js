import { useEffect, memo } from 'react';

import { useDispatch } from 'react-redux';

import { clientsAsync } from '../actions/usersActions';

const ClientsListCall = () => {
  // ** Store Vars
  const dispatch = useDispatch();

  // ** Get data on mount
  useEffect(() => {
    dispatch(clientsAsync());
  }, [dispatch]);

  return null;
};

export default memo(ClientsListCall);
