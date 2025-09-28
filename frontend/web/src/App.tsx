import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { SnackbarProvider } from 'notistack';
import { QueryProvider } from './providers/QueryProvider';
import { AppThemeProvider } from './contexts/ThemeContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import ErrorBoundary from './components/error/ErrorBoundary';
import ProtectedRoute from './components/auth/ProtectedRoute';
import GlobalLayout from './components/layout/GlobalLayout';
import { FRONTEND_ROUTES } from './config/routingRegistry';
import Dashboard from './pages/Dashboard';
import Accounts from './pages/Accounts';
import Transactions from './pages/Transactions';
import Analytics from './pages/Analytics';
import Admin from './pages/Admin';
import Profile from './pages/Profile';
import Settings from './pages/Settings';
import Reports from './pages/Reports';
import { LoginForm, RegisterForm } from './components/auth';
import FrenlyAISSOT from './components/ai/FrenlyAISSOT';
import SSOTManager from './components/ssot/SSOTManager';
import PerformanceDashboard from './components/monitoring/PerformanceDashboard';
import SystemDashboard from './components/monitoring/SystemDashboard';
import { Box, Container, Typography, Button } from '@mui/material';

interface RegisterFormData {
  firstName: string;
  lastName: string;
  email: string;
  username: string;
  password: string;
  confirmPassword: string;
}

// Main App Component
const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <QueryProvider>
        <AppThemeProvider>
          <SnackbarProvider maxSnack={3}>
            <AuthProvider>
              <Router>
                <AppContent />
              </Router>
            </AuthProvider>
          </SnackbarProvider>
        </AppThemeProvider>
      </QueryProvider>
    </ErrorBoundary>
  );
};

// App Content Component
const AppContent: React.FC = () => {
  const { user } = useAuth();

  // Generate routes from registry
  const generateRoutes = () => {
    return FRONTEND_ROUTES.map((route) => {
      const Component = getComponentByName(route.component);
      
      if (route.requiresAuth) {
        return (
          <Route
            key={route.id}
            path={route.path}
            element={
              <ProtectedRoute>
                <GlobalLayout>
                  <Component />
                </GlobalLayout>
              </ProtectedRoute>
            }
          />
        );
      } else {
        return (
          <Route
            key={route.id}
            path={route.path}
            element={
              <GlobalLayout>
                <Component />
              </GlobalLayout>
            }
          />
        );
      }
    });
  };

  return (
    <Routes>
      {generateRoutes()}
      
      {/* Default redirect */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      
      {/* 404 Fallback */}
      <Route path="*" element={
        <GlobalLayout>
          <NotFoundPage />
        </GlobalLayout>
      } />
    </Routes>
  );
};

// Component mapping function
const getComponentByName = (componentName: string) => {
  const componentMap: { [key: string]: React.ComponentType } = {
    Dashboard,
    Accounts,
    Transactions,
    Analytics,
    Reports,
    Admin,
    Profile,
    Settings,
    Security: Settings, // Alias for security settings
    LoginPage,
    RegisterPage,
    SSOTManager,
    SystemDashboard,
    PerformanceDashboard,
    // Add more components as needed
  };
  
  return componentMap[componentName] || Dashboard;
};

// 404 Not Found Page
const NotFoundPage: React.FC = () => {
  return (
    <Container maxWidth="md" sx={{ py: 8, textAlign: 'center' }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h1" sx={{ fontSize: '4rem', fontWeight: 'bold', color: 'primary.main' }}>
          404
        </Typography>
        <Typography variant="h4" gutterBottom>
          Page Not Found
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          The page you're looking for doesn't exist or has been moved.
        </Typography>
      </Box>
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
        <Button variant="contained" onClick={() => window.history.back()}>
          Go Back
        </Button>
        <Button variant="outlined" onClick={() => window.location.href = '/dashboard'}>
          Go to Dashboard
        </Button>
      </Box>
    </Container>
  );
};

// Login Page Component
const LoginPage: React.FC = () => {
  const { login, isLoading } = useAuth();

  const handleLogin = async (data: { email: string; password: string }) => {
    try {
      await login(data.email, data.password);
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
      bgcolor="background.default"
    >
      <Container maxWidth="sm">
        <Box maxWidth={400} width="100%" p={3} mx="auto">
          <LoginForm onSubmit={handleLogin} loading={isLoading} />
        </Box>
      </Container>
    </Box>
  );
};

// Register Page Component
const RegisterPage: React.FC = () => {
  const { register, isLoading } = useAuth();

  const handleRegister = async (data: RegisterFormData) => {
    try {
      await register(data);
    } catch (error) {
      console.error('Registration failed:', error);
    }
  };

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
      bgcolor="background.default"
    >
      <Container maxWidth="sm">
        <Box maxWidth={400} width="100%" p={3} mx="auto">
          <RegisterForm onSubmit={handleRegister} loading={isLoading} />
        </Box>
      </Container>
    </Box>
  );
};

export default App;