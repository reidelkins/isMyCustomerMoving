import React from 'react';
import PropTypes from 'prop-types';
import { Route, Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { showLoginInfo } from '../redux/actions/authActions';

PrivateRoute.propTypes = {
  component: PropTypes.elementType.isRequired,
};

const PrivateRoute = ({ component: Component, ...rest }) => {
  const userLogin = useSelector(showLoginInfo);
  const { userInfo } = userLogin;
  return <Route {...rest} render={(props) => (userInfo ? <Component {...props} /> : <Navigate to="/login" />)} />;
};

export default PrivateRoute;
