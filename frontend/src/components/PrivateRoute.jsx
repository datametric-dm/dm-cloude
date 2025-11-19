import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

export default function PrivateRoute({ children }) {
  const token = localStorage.getItem('access_token');
  const location = useLocation();
  
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  // Allow access to /companies page without company selected
  if (location.pathname === '/companies') {
    return children;
  }

  // For other routes, check if company is selected
  const currentCompany = localStorage.getItem('current_company');
  if (!currentCompany && location.pathname !== '/companies') {
    return <Navigate to="/companies" replace />;
  }
  
  return children;
}
