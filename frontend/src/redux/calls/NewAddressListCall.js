import { useEffect, memo } from 'react';

import { useDispatch } from 'react-redux';

import { newAddressAsync } from '../actions/usersActions';

const NewAddressListCall = () => {
  // ** Store Vars
  const dispatch = useDispatch();

  // ** Get data on mount
  useEffect(() => {
    dispatch(newAddressAsync(1));
  }, [dispatch]);

  return null;
};

export default memo(NewAddressListCall);
