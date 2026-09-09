import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useApp } from '../context/AppContext';

/** Prevents demo state from being rendered as a signed-in learner session. */
export const ProtectedRoute: React.FC = () => {
  const { authToken, isExchangingTicket } = useApp();
  const location = useLocation();

  if (isExchangingTicket) {
    return (
      <div className="min-h-screen w-screen bg-[#090a0f] flex items-center justify-center p-4">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-4 border-purple-500/30 border-t-purple-500 rounded-full animate-spin" />
          <p className="text-sm font-semibold text-slate-300">Authenticating GrowthOS Session...</p>
        </div>
      </div>
    );
  }

  if (!authToken) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <Outlet />;
};
