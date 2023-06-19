import { useEffect, useState, memo } from 'react';

import { useDispatch } from 'react-redux';

import { recentlySoldAsync } from '../actions/usersActions';

const RecentlySoldListCall = () => {
  // ** Store Vars
  const dispatch = useDispatch();

  // ** Get data on mount
  useEffect(() => {
    dispatch(recentlySoldAsync(1));
  }, [dispatch]);

  return null;
};

export default memo(RecentlySoldListCall);
