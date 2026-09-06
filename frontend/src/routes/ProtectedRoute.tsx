import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useApp } from '../context/AppContext';

/** Prevents demo state from being rendered as a signed-in learner session. */
export const ProtectedRoute: React.FC = () => {
  const { authToken } = useApp();
  const location = useLocation();

  if (!authToken) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <Outlet />;
};
