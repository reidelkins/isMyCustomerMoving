import PropTypes from 'prop-types';
import { useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';
import { showLoginInfo } from '../redux/actions/authActions';

function ProtectedRoute({ children }) {
  const userLogin = useSelector(showLoginInfo);
  const { userInfo } = userLogin;

  if (!userInfo) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

ProtectedRoute.propTypes = {
  children: PropTypes.oneOfType([PropTypes.arrayOf(PropTypes.node), PropTypes.node]).isRequired,
};

export default ProtectedRoute;
