import { Navigate, useRoutes } from 'react-router-dom';
// layouts
import DashboardLayout from './layouts/dashboard';
import LogoOnlyLayout from './layouts/LogoOnlyLayout';
//
import CustomerData from './pages/CustomerData';
import RecentlySoldData from './pages/RecentlySoldData';
import Login from './pages/Login';
import Validate2fa from './pages/Validate2fa';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/NewPassword';
import NotFound from './pages/Page404';
import Register from './pages/Register';
import AddUser from './pages/AddUser';
import Referrals from './pages/Referrals';

import ProfileSettings from './pages/ProfileSettings';
import PrivacyPolicy from './pages/PrivacyPolicy';
import TermsOfService from './pages/TermsOfService';

// ----------------------------------------------------------------------

export default function Router() {
  return useRoutes([
    {
      path: '/dashboard',
      element: <DashboardLayout />,
      children: [
        // { path: '', element:<PrivateRoute path="/dashboard/customers" component={<Navigate to="/dashboard/customers" />} />},
        { path: '', element: <Navigate to="/dashboard/customers" /> },
        // { path: 'settings', element: <PrivateRoute path="/dashboard/settings" component={<ProfileSettings />} />},
        { path: 'settings', element: <ProfileSettings /> },
        // { path: 'customers', element: <PrivateRoute path="/dashboard/customers" component={<CustomerData />} /> },
        { path: 'customers', element: <CustomerData /> },
        { path: 'recentlysold', element: <RecentlySoldData />},
        { path: 'referrals', element: <Referrals />},
        // { path: 'adduser', element: <PrivateRoute path="/dashboard/adduser" component={<AddUser />} />}
        { path: 'adduser', element: <AddUser />},
      ],
    },
    {
      path: '/',
      element: <LogoOnlyLayout />,
      children: [
        { path: '/', element: <Navigate to="/dashboard/customers" /> },
        { path: 'login', element: <Login /> },
        { path: 'validate2fa', element: <Validate2fa />},
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
    { path: '*', element: <Navigate to="/404" replace /> },
  ]);
}
