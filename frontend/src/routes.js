import { Navigate, useRoutes } from 'react-router-dom';
// layouts
import DashboardLayout from './layouts/dashboard';
import LogoOnlyLayout from './layouts/LogoOnlyLayout';
//
import Home from './pages/Home';
import RecentlySoldData from './pages/RecentlySoldData';
import Login from './pages/Login';
import Logout from './pages/Logout';
import Validate2fa from './pages/Validate2fa';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/NewPassword';
import NotFound from './pages/Page404';
import Register from './pages/Register';
import AddUser from './pages/AddUser';
import Referrals from './pages/Referrals';
import EnterpriseSettings from './pages/EnterpriseSettings';
import ProfileSettings from './pages/ProfileSettings';
import PrivacyPolicy from './pages/PrivacyPolicy';
import TermsOfService from './pages/TermsOfService';


export default function Router() {
  return useRoutes([
    {
      path: '/',
      element: <LogoOnlyLayout />,
      children: [
        { path: '/', element: <Navigate to="/dashboard" /> },
        { path: 'login', element: <Login /> },
        { path: 'logout', element: <Logout />},
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
    {
      path: '/dashboard',
      element: <DashboardLayout />,
      children: [
        { path: '', element: <Home /> },
        { path: 'settings/user', element: <ProfileSettings />} ,
        { path: 'settings/enterprise', element: <EnterpriseSettings />} ,
        { path: 'recentlysold', element: <RecentlySoldData />},
        { path: 'referrals', element: <Referrals />},
        { path: 'adduser', element: <AddUser />},
        
      ],
    },
    { path: '*', element: <Navigate to="/404" replace /> },
  ]);
}
