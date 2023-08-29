// import PropTypes from 'prop-types';
// import { useSelector } from 'react-redux';
// import { Navigate } from 'react-router-dom';
// import { showLoginInfo } from '../redux/actions/authActions';
import React, {useEffect} from "react";
import { useRownd } from "@rownd/react";
import axios from "axios";

function ProtectedRoute() {
  // const userLogin = useSelector(showLoginInfo);
  // const { userInfo } = userLogin;
  const { is_authenticated: isAuthenticated, user, requestSignIn, getAccessToken } = useRownd();
  console.log(isAuthenticated)
  useEffect(() => {
    if (!isAuthenticated) {
      console.log("revisiting")
      // requestSignIn();
    }
  }, [isAuthenticated]);

  const 
  const test() => {
    console.log(getAccessToken())

  }

  return (
    <div>
      {isAuthenticated ? (
        <div>
          <h1>Welcome {user.data.full_name}</h1>
          <button onClick={test()}>Get access token</button>
        </div>
      ) : (
        <div>
          <h1>Please sign in to continue</h1>
        </div>
      )}
    </div>
  );

  // if (!userInfo) {
  //   return <Navigate to="/login" replace />;
  // }

  // return <>{children}</>;
}

// ProtectedRoute.propTypes = {
//   children: PropTypes.oneOfType([PropTypes.arrayOf(PropTypes.node), PropTypes.node]).isRequired,
// };

export default ProtectedRoute;
