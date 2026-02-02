// src/App.jsx
import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useStore } from './store/useStore.js';

import Login from './components/Login.jsx';
import Signup from './components/Signup.jsx';
import ForgotPassword from './components/ForgotPassword.jsx';
import ResetPassword from './components/ResetPassword.jsx';
import Onboarding from './components/Onboarding.jsx';
import Dashboard from './components/Dashboard.jsx';
import BentoHome from './components/BentoHome.jsx';
import AssessmentPortal from './components/AssessmentPortal.jsx';
import ResultsPage from './components/ResultsPage.jsx';
import UserProfile from './components/UserProfile.jsx';
import GeneratingReportPage from './components/GeneratingReportPage.jsx';
import DailyReflectionPage from './components/DailyReflectionPage.jsx';
import JourneyOverviewPage from './components/JourneyOverviewPage.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import ErrorBoundary from './components/ErrorBoundary.jsx';
import AppLayout from './components/AppLayout.jsx';

export default function App() {
  const { initializeAuth } = useStore();

  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  return (
    <ErrorBoundary>
      <BrowserRouter>
        <div className="page-transition">
          <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password/:token" element={<ResetPassword />} />

            <Route
              path="/onboarding"
              element={
                <ProtectedRoute>
                  <Onboarding />
                </ProtectedRoute>
              }
            />

            {/* Home/Bento Dashboard */}
            <Route
              path="/home"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <BentoHome />
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <Dashboard />
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/assessment/:testId"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <AssessmentPortal />
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/results/:submissionId"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <ResultsPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/report/generating/:submissionId"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <GeneratingReportPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <UserProfile />
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/journey"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <JourneyOverviewPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/journey/day/:dayNumber"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <DailyReflectionPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </BrowserRouter>
    </ErrorBoundary>
  );
}