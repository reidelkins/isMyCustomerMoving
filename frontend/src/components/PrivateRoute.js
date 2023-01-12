import React from 'react';
import { Route, Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { showLoginInfo } from '../redux/actions/authActions';

const PrivateRoute = ({ component: Component, ...rest }) => {
    const userLogin = useSelector(showLoginInfo);
    const { userInfo } = userLogin;
    return (
        <Route
            {...rest}
            render={props =>
                userInfo ? (
                    <Component {...props} />
                ) : (
                    <Navigate to="/login" />
                )
            }
        />
    );
};

export default PrivateRoute;