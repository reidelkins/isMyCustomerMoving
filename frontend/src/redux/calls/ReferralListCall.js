import { useEffect, useState, memo } from 'react';

import { useDispatch } from 'react-redux';


import { referralsAsync } from '../actions/usersActions';

const ReferralsListCall = () => {
  // ** Store Vars
  const dispatch = useDispatch();
  
  



  // ** Get data on mount
  useEffect(() => {
    dispatch(referralsAsync(1));
  }, [dispatch]);

  return null;
};

export default memo(ReferralsListCall);
