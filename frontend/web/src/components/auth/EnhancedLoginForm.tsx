import React, { useState } from "react";
import {
  Box,
  Typography,
  Alert,
  Divider,
  IconButton,
  Tooltip,
  Card,
  CardContent,
  Grid,
} from "@mui/material";
import {
  Google as GoogleIcon,
  Microsoft as MicrosoftIcon,
  LinkedIn as LinkedInIcon,
  GitHub as GitHubIcon,
  Visibility,
  VisibilityOff,
} from "@mui/icons-material";
import { FormField, Button } from "../ui";
import { useFormValidation, FormData } from "../../hooks/useFormValidation";

interface EnhancedLoginFormProps {
  onSubmit: (data: { email: string; password: string }) => Promise<void>;
  onOAuthLogin: (provider: string, accessToken: string) => Promise<void>;
  loading?: boolean;
  error?: string;
}

const OAuthProviders = [
  {
    id: "google",
    name: "Google",
    icon: <GoogleIcon />,
    color: "#4285f4",
    description: "Sign in with Google",
  },
  {
    id: "microsoft",
    name: "Microsoft",
    icon: <MicrosoftIcon />,
    color: "#0078d4",
    description: "Sign in with Microsoft",
  },
  {
    id: "linkedin",
    name: "LinkedIn",
    icon: <LinkedInIcon />,
    color: "#0077b5",
    description: "Sign in with LinkedIn",
  },
  {
    id: "github",
    name: "GitHub",
    icon: <GitHubIcon />,
    color: "#333",
    description: "Sign in with GitHub",
  },
];

const EnhancedLoginForm: React.FC<EnhancedLoginFormProps> = ({
  onSubmit,
  onOAuthLogin,
  loading = false,
  error,
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [oauthLoading, setOauthLoading] = useState<string | null>(null);

  const validationRules = {
    email: {
      required: true,
      email: true,
    },
    password: {
      required: true,
      minLength: 6,
    },
  };

  const { formData, handleChange, handleBlur, handleSubmit, getFieldError } =
    useFormValidation({ email: "", password: "" }, validationRules);

  const handleFormSubmit = async (data: FormData) => {
    setIsSubmitting(true);
    try {
      await onSubmit({
        email: data.email,
        password: data.password,
      });
    } catch (_err) {
      // Error is handled by parent component
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOAuthLogin = async (provider: string) => {
    setOauthLoading(provider);
    try {
      // In a real implementation, this would open OAuth popup or redirect
      // For now, we'll simulate the OAuth flow
      const mockAccessToken = `mock_${provider}_token_${Date.now()}`;
      await onOAuthLogin(provider, mockAccessToken);
    } catch (_err) {
      // Error is handled by parent component
    } finally {
      setOauthLoading(null);
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit(handleFormSubmit)}
      sx={{
        maxWidth: 500,
        margin: "0 auto",
        p: 3,
        display: "flex",
        flexDirection: "column",
        gap: 2,
      }}
    >
      <Typography variant="h4" component="h1" textAlign="center" gutterBottom>
        Welcome to NEXUS
      </Typography>
      <Typography
        variant="body2"
        color="text.secondary"
        textAlign="center"
        sx={{ mb: 2 }}
      >
        Sign in to access your financial examination platform
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* OAuth Login Options */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom textAlign="center">
          Quick Sign In
        </Typography>
        <Grid container spacing={2}>
          {OAuthProviders.map((provider) => (
            <Grid item xs={6} sm={3} key={provider.id}>
              <Tooltip title={provider.description}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={provider.icon}
                  onClick={() => handleOAuthLogin(provider.id)}
                  disabled={loading || oauthLoading === provider.id}
                  sx={{
                    borderColor: provider.color,
                    color: provider.color,
                    "&:hover": {
                      borderColor: provider.color,
                      backgroundColor: `${provider.color}10`,
                    },
                    minHeight: 48,
                  }}
                >
                  {oauthLoading === provider.id ? "..." : provider.name}
                </Button>
              </Tooltip>
            </Grid>
          ))}
        </Grid>
      </Box>

      <Divider sx={{ my: 2 }}>
        <Typography variant="body2" color="text.secondary">
          OR
        </Typography>
      </Divider>

      {/* Traditional Login Form */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Email & Password
        </Typography>

        <FormField
          name="email"
          label="Email Address"
          type="email"
          value={formData.email}
          onChange={(value) => handleChange("email", value)}
          onBlur={() => handleBlur("email")}
          error={!!getFieldError("email")}
          required
          fullWidth
          autoComplete="email"
          autoFocus
          sx={{ marginBottom: 2 }}
        />

        <FormField
          name="password"
          label="Password"
          type={showPassword ? "text" : "password"}
          value={formData.password}
          onChange={(value) => handleChange("password", value)}
          onBlur={() => handleBlur("password")}
          error={!!getFieldError("password")}
          required
          fullWidth
          autoComplete="current-password"
          InputProps={{
            endAdornment: (
              <IconButton
                aria-label="toggle password visibility"
                onClick={togglePasswordVisibility}
                edge="end"
              >
                {showPassword ? <VisibilityOff /> : <Visibility />}
              </IconButton>
            ),
          }}
        />
      </Box>

      {/* Submit Button */}
      <Button
        type="submit"
        variant="primary"
        size="large"
        loading={loading || isSubmitting}
        disabled={loading || isSubmitting}
        fullWidth
        sx={{ mb: 2 }}
      >
        {loading || isSubmitting ? "Signing In..." : "Sign In"}
      </Button>

      {/* Additional Options */}
      <Box sx={{ textAlign: "center" }}>
        <Typography variant="body2" color="text.secondary">
          Don&apos;t have an account?{" "}
          <Typography
            component="a"
            href="/register"
            variant="body2"
            color="primary"
            sx={{
              textDecoration: "none",
              "&:hover": { textDecoration: "underline" },
            }}
          >
            Sign up here
          </Typography>
        </Typography>
      </Box>

      {/* Security Notice */}
      <Card sx={{ mt: 2, backgroundColor: "background.paper" }}>
        <CardContent sx={{ p: 2, "&:last-child": { pb: 2 } }}>
          <Typography variant="body2" color="text.secondary" textAlign="center">
            🔒 Your data is protected with enterprise-grade security and
            encryption
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default EnhancedLoginForm;
