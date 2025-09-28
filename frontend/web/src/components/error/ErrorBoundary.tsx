import React, { Component, ErrorInfo, ReactNode } from "react";
import {
  Box,
  Typography,
  Button,
  Paper,
  Alert,
  AlertTitle,
} from "@mui/material";
import {
  Refresh as RefreshIcon,
  BugReport as BugIcon,
} from "@mui/icons-material";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({
      error,
      errorInfo,
    });

    // Log error to console in development
    if (process.env.NODE_ENV === "development") {
      console.error("ErrorBoundary caught an error:", error, errorInfo);
    }

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Log error to external service in production
    if (process.env.NODE_ENV === "production") {
      // TODO: Send error to logging service
      console.error("Production error:", error, errorInfo);
    }
  }

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <Box
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          minHeight="100vh"
          p={3}
        >
          <Paper
            elevation={3}
            sx={{
              p: 4,
              maxWidth: 600,
              width: "100%",
              textAlign: "center",
            }}
          >
            <Box mb={3}>
              <BugIcon sx={{ fontSize: 64, color: "error.main", mb: 2 }} />
              <Typography variant="h4" component="h1" gutterBottom>
                Oops! Something went wrong
              </Typography>
              <Typography variant="body1" color="text.secondary" paragraph>
                We&apos;re sorry, but something unexpected happened. Please try
                refreshing the page.
              </Typography>
            </Box>

            {process.env.NODE_ENV === "development" && this.state.error && (
              <Alert severity="error" sx={{ mb: 3, textAlign: "left" }}>
                <AlertTitle>Error Details</AlertTitle>
                <Typography
                  variant="body2"
                  component="pre"
                  sx={{ whiteSpace: "pre-wrap" }}
                >
                  {this.state.error.toString()}
                </Typography>
                {this.state.errorInfo && (
                  <Typography
                    variant="body2"
                    component="pre"
                    sx={{ whiteSpace: "pre-wrap", mt: 1 }}
                  >
                    {this.state.errorInfo.componentStack}
                  </Typography>
                )}
              </Alert>
            )}

            <Box display="flex" gap={2} justifyContent="center">
              <Button
                variant="contained"
                startIcon={<RefreshIcon />}
                onClick={this.handleRetry}
              >
                Try Again
              </Button>
              <Button
                variant="outlined"
                onClick={() => window.location.reload()}
              >
                Refresh Page
              </Button>
            </Box>
          </Paper>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
