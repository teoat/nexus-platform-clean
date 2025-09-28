import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { SnackbarProvider } from "notistack";
import { QueryProvider } from "./providers/QueryProvider";
import { AppThemeProvider } from "./contexts/ThemeContext";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import ErrorBoundary from "./components/error/ErrorBoundary";
import ProtectedRoute from "./components/auth/ProtectedRoute";
import Dashboard from "./pages/Dashboard";
import { LoginForm, RegisterForm } from "./components/auth";
import { ThemeSwitcher } from "./components/ui";
import { Box, AppBar, Toolbar, Typography } from "@mui/material";

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
  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            NEXUS Platform
          </Typography>
          <ThemeSwitcher />
        </Toolbar>
      </AppBar>

      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Protected Routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* Individual Dashboard Routes */}
        <Route
          path="/dashboard/main-control"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard/ai-intelligence"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard/user-experience"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Box>
  );
};

// Login Page Component
const LoginPage: React.FC = () => {
  const { login, isLoading } = useAuth();

  const handleLogin = async (data: { email: string; password: string }) => {
    try {
      await login(data.email, data.password);
    } catch (error) {
      console.error("Login failed:", error);
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
      <Box maxWidth={400} width="100%" p={3}>
        <LoginForm onSubmit={handleLogin} loading={isLoading} />
      </Box>
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
      console.error("Registration failed:", error);
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
      <Box maxWidth={400} width="100%" p={3}>
        <RegisterForm onSubmit={handleRegister} loading={isLoading} />
      </Box>
    </Box>
  );
};

export default App;
