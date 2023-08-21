import { useEffect, memo } from 'react';

import { useDispatch } from 'react-redux';

import { realtorAsync } from '../actions/usersActions';

const RealtorListCall = () => {
  // ** Store Vars
  const dispatch = useDispatch();

  // ** Get data on mount
  useEffect(() => {
    dispatch(realtorAsync(1));
  }, [dispatch]);

  return null;
};

export default memo(RealtorListCall);
