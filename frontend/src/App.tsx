import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
// Lazy load route components with correct default export
const LoginPage = lazy(() => import('./pages/LoginPage').then(m => ({ default: m.LoginPage })));
const RegisterPage = lazy(() => import('./pages/RegisterPage').then(m => ({ default: m.RegisterPage })));
const HomePage = lazy(() => import('./pages/HomePage').then(m => ({ default: m.HomePage })));
const TopSuggestionsPage = lazy(() => import('./pages/TopSuggestionsPage').then(m => ({ default: m.TopSuggestionsPage })));
const NewSuggestionPage = lazy(() => import('./pages/NewSuggestionPage').then(m => ({ default: m.NewSuggestionPage })));
const Layout = lazy(() => import('./components/Layout').then(m => ({ default: m.Layout })));
const ProtectedRoute = lazy(() => import('./components/ProtectedRoute').then(m => ({ default: m.ProtectedRoute })));

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Suspense fallback={<div className="flex justify-center items-center min-h-screen">Loading...</div>}>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            {/* Protected routes */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Layout>
                    <HomePage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/top"
              element={
                <ProtectedRoute>
                  <Layout>
                    <TopSuggestionsPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/new"
              element={
                <ProtectedRoute>
                  <Layout>
                    <NewSuggestionPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            {/* Redirect to home for unknown routes */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App; 