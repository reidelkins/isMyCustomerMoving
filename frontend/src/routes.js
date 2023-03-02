import { Navigate, useRoutes } from 'react-router-dom';
// layouts
import LogoOnlyLayout from './layouts/LogoOnlyLayout';
// pages
import Maintenance from './pages/Maintenance';

// ----------------------------------------------------------------------

export default function Router() {
  return useRoutes([
    {
      path: '/maintenance',
      element: <LogoOnlyLayout />,
      children: [
        { path: '', element: <Maintenance /> },        
      ],
    },    
    { path: '*', element: <Navigate to="/maintenance" replace /> },
  ]);
}
