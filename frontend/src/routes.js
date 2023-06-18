import { Navigate, useRoutes } from 'react-router-dom';
// layouts
import DashboardLayout from './layouts/dashboard';
import LogoOnlyLayout from './layouts/LogoOnlyLayout';
//
import Home from './pages/dashboard/Home';
import RecentlySoldData from './pages/dashboard/RecentlySoldData';
import Login from './pages/root/Login';
import Logout from './pages/root/Logout';
import Validate2fa from './pages/root/Validate2fa';
import ForgotPassword from './pages/root/ForgotPassword';
import ResetPassword from './pages/root/NewPassword';
import NotFound from './pages/root/Page404';
import Register from './pages/root/Register';
import AddUser from './pages/root/AddUser';
import Referrals from './pages/dashboard/Referrals';
import EnterpriseSettings from './pages/dashboard/settings/EnterpriseSettings';
import ProfileSettings from './pages/dashboard/settings/ProfileSettings';
import PrivacyPolicy from './pages/root/PrivacyPolicy';
import TermsOfService from './pages/root/TermsOfService';

export default function Router() {
  return useRoutes([
    {
      path: '/',
      element: <LogoOnlyLayout />,
      children: [
        { path: '/', element: <Navigate to="/dashboard" /> },
        { path: 'login', element: <Login /> },
        { path: 'logout', element: <Logout /> },
        { path: 'validate2fa', element: <Validate2fa /> },
        { path: 'register/:company?/:accesstoken?', element: <Register /> },
        { path: 'addeduser/:token', element: <AddUser /> },
        { path: 'forgot_password', element: <ForgotPassword /> },
        { path: 'resetpassword/:token', element: <ResetPassword /> },
        { path: 'termsofservice', element: <TermsOfService /> },
        { path: 'privacypolicy', element: <PrivacyPolicy /> },
        { path: '404', element: <NotFound /> },
        { path: '*', element: <Navigate to="/404" /> },
      ],
    },
    {
      path: '/dashboard',
      element: <DashboardLayout />,
      children: [
        { path: '', element: <Home /> },
        { path: 'settings/user', element: <ProfileSettings /> },
        { path: 'settings/enterprise', element: <EnterpriseSettings /> },
        { path: 'recentlysold', element: <RecentlySoldData /> },
        { path: 'referrals', element: <Referrals /> },
        { path: 'adduser', element: <AddUser /> },
      ],
    },
    { path: '*', element: <Navigate to="/404" replace /> },
  ]);
}
