import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Landing } from '../pages/Landing/Landing';
import { Login } from '../pages/Login/Login';
import { Signup } from '../pages/Signup/Signup';
import { Onboarding } from '../pages/Onboarding/Onboarding';

import { AppLayout } from '../components/layout/AppLayout';
import { Dashboard } from '../pages/Dashboard/Dashboard';
import { IdentityTwin } from '../pages/IdentityTwin/IdentityTwin';
import { Learning } from '../pages/Learning/Learning';
import { Opportunity } from '../pages/Opportunity/Opportunity';
import { Planner } from '../pages/Planner/Planner';
import { Reflection } from '../pages/Reflection/Reflection';
import { Notifications } from '../pages/Notifications/Notifications';
import { Analytics } from '../pages/Analytics/Analytics';
import { Profile } from '../pages/Profile/Profile';

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Public Pages */}
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/onboarding" element={<Onboarding />} />

      {/* Authenticated Dashboard Layout */}
      <Route element={<AppLayout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/identity-twin" element={<IdentityTwin />} />
        <Route path="/learning" element={<Learning />} />
        <Route path="/opportunities" element={<Opportunity />} />
        <Route path="/planner" element={<Planner />} />
        <Route path="/reflection" element={<Reflection />} />
        <Route path="/notifications" element={<Notifications />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/profile" element={<Profile />} />
      </Route>

      {/* Fallback redirect */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};
