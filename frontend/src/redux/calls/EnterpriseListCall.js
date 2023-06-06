import { useEffect, memo } from 'react';

import { useDispatch } from 'react-redux';

import { enterpriseAsync } from '../actions/enterpriseActions';


const EnterpriseCall = () => {
  // ** Store Vars
  const dispatch = useDispatch();

  // ** Get data on mount
  useEffect(() => {
    dispatch(enterpriseAsync());
    
  }, [dispatch]);

  return null;
};

export default memo(EnterpriseCall);
