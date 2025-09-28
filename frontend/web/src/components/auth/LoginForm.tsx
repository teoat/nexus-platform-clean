import React, { useState } from "react";
import { Box, Typography, Alert } from "@mui/material";
import { FormField } from "../ui";
import { Button } from "../ui";
import { useFormValidation, FormData } from "../../hooks/useFormValidation";

interface LoginFormProps {
  onSubmit: (data: { email: string; password: string }) => Promise<void>;
  loading?: boolean;
  error?: string;
}

const LoginForm: React.FC<LoginFormProps> = ({
  onSubmit,
  loading = false,
  error,
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);

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
    } catch (err) {
      // Error is handled by parent component
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit(handleFormSubmit)}
      sx={{
        maxWidth: 400,
        margin: "0 auto",
        p: 3,
        display: "flex",
        flexDirection: "column",
        gap: 2,
      }}
    >
      <Typography variant="h4" component="h1" textAlign="center" gutterBottom>
        Sign In to NEXUS
      </Typography>
      <Typography
        variant="body2"
        color="text.secondary"
        textAlign="center"
        sx={{ mb: 2 }}
      >
        Enter your credentials to access your account
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

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
      />

      <FormField
        name="password"
        label="Password"
        type="password"
        value={formData.password}
        onChange={(value) => handleChange("password", value)}
        onBlur={() => handleBlur("password")}
        error={!!getFieldError("password")}
        required
        fullWidth
        autoComplete="current-password"
      />

      <Box sx={{ mt: 3, display: "flex", justifyContent: "center" }}>
        <Button
          type="submit"
          variant="primary"
          size="large"
          loading={loading || isSubmitting}
          disabled={loading || isSubmitting}
          fullWidth
        >
          Sign In
        </Button>
      </Box>

      <Box sx={{ mt: 2, textAlign: "center" }}>
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
    </Box>
  );
};

export default LoginForm;
