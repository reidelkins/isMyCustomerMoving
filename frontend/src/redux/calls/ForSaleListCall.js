import { useEffect, memo } from 'react';

import { useDispatch } from 'react-redux';

import { forSaleAsync } from '../actions/usersActions';

const ForSaleListCall = () => {
  // ** Store Vars
  const dispatch = useDispatch();

  // ** Get data on mount
  useEffect(() => {
    dispatch(forSaleAsync(1));
  }, [dispatch]);

  return null;
};

export default memo(ForSaleListCall);
