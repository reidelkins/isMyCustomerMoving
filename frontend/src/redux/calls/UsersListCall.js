import { Fragment, useEffect, memo } from 'react';

import { useDispatch } from 'react-redux';

import { usersAsync, updateCompany } from '../actions/usersActions';

const UsersListCall = () => {
  // ** Store Vars
  const dispatch = useDispatch();

  // ** Get data on mount
  useEffect(() => {
    dispatch(usersAsync());
  }, [dispatch]);

  return null;
};

export default memo(UsersListCall);
