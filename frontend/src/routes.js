import { Navigate, useRoutes } from 'react-router-dom';
// layouts
import DashboardLayout from './layouts/dashboard';
import LogoOnlyLayout from './layouts/LogoOnlyLayout';
//
// import Dashboard from './pages/dashboard/Home';
import CustomerData from './pages/dashboard/CustomerData';
import ForSaleData from './pages/dashboard/ForSaleData';
import RecentlySoldData from './pages/dashboard/RecentlySoldData';
import Login from './pages/root/Login';
import Logout from './pages/root/Logout';
import Validate2fa from './pages/account/Validate2fa';
import ForgotPassword from './pages/root/ForgotPassword';
import ResetPassword from './pages/root/NewPassword';
import NotFound from './pages/root/Page404';
import Register from './pages/root/Register';
import AddUser from './pages/root/AddUser';
import Referrals from './pages/dashboard/Referrals';
import EnterpriseSettings from './pages/dashboard/settings/EnterpriseSettings';
import ProfileSettings from './pages/dashboard/settings/ProfileSettings';
import PrivacyPolicy from './pages/account/PrivacyPolicy';
import TermsOfService from './pages/account/TermsOfService';
import ProtectedRoute from './components/ProtectedRoute';

export default function Router() {
  return useRoutes([
    {
      path: '/',
      element: <LogoOnlyLayout />,
      children: [
        { path: '/', element: <Navigate to="/dashboard" /> },
        { path: 'login', element: <Login /> },
        { path: 'logout', element: <Logout /> },
        { path: 'register/:company?/:access_token?', element: <Register /> },
        { path: 'addeduser/:token', element: <AddUser /> },
        { path: 'forgot_password', element: <ForgotPassword /> },
        { path: 'resetpassword/:token', element: <ResetPassword /> },
        { path: '404', element: <NotFound /> },
        { path: '*', element: <Navigate to="/404" /> },
      ],
    },
    {
      path: '/dashboard',
      element: (
        <ProtectedRoute>
          <DashboardLayout />
        </ProtectedRoute>
      ),
      children: [
        { path: '', element: <CustomerData /> },
        // { path: 'customers', element: <CustomerData /> },
        { path: 'settings/user', element: <ProfileSettings /> },
        { path: 'settings/enterprise', element: <EnterpriseSettings /> },
        { path: 'forsale', element: <ForSaleData /> },
        { path: 'recentlysold', element: <RecentlySoldData /> },
        { path: 'referrals', element: <Referrals /> },
        { path: 'adduser', element: <AddUser /> },
      ],
    },
    {
      path: '/account',
      element: (
        <ProtectedRoute>
          <LogoOnlyLayout />
        </ProtectedRoute>
      ),
      children: [
        { path: 'validate2fa', element: <Validate2fa /> },
        { path: 'termsofservice', element: <TermsOfService /> },
        { path: 'privacypolicy', element: <PrivacyPolicy /> },
      ],
    },
    { path: '*', element: <Navigate to="/404" replace /> },
  ]);
}
