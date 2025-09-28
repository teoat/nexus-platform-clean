import React, { useState } from "react";
import { Box, Typography, Alert } from "@mui/material";
import { Form, FormField, Button } from "../ui";
import { useFormValidation, FormData } from "../../hooks/useFormValidation";

interface RegisterFormProps {
  onSubmit: (data: RegisterFormData) => Promise<void>;
  loading?: boolean;
  error?: string;
}

interface RegisterFormData {
  firstName: string;
  lastName: string;
  email: string;
  username: string;
  password: string;
  confirmPassword: string;
}

const RegisterForm: React.FC<RegisterFormProps> = ({
  onSubmit,
  loading = false,
  error,
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validationRules = {
    firstName: {
      required: true,
      minLength: 2,
      maxLength: 50,
    },
    lastName: {
      required: true,
      minLength: 2,
      maxLength: 50,
    },
    email: {
      required: true,
      email: true,
    },
    username: {
      required: true,
      minLength: 3,
      maxLength: 30,
      pattern: /^[a-zA-Z0-9_]+$/,
    },
    password: {
      required: true,
      minLength: 8,
      pattern:
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
    },
    confirmPassword: {
      required: true,
      custom: (value: string) => {
        const password = formData.password;
        if (value !== password) {
          return "Passwords do not match";
        }
        return null;
      },
    },
  };

  const { formData, handleChange, handleBlur, handleSubmit, getFieldError } =
    useFormValidation(
      {
        firstName: "",
        lastName: "",
        email: "",
        username: "",
        password: "",
        confirmPassword: "",
      },
      validationRules,
    );

  const handleFormSubmit = async (data: FormData) => {
    setIsSubmitting(true);
    try {
      await onSubmit({
        firstName: data.firstName,
        lastName: data.lastName,
        email: data.email,
        username: data.username,
        password: data.password,
        confirmPassword: data.confirmPassword,
      });
    } catch (err) {
      // Error is handled by parent component
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Form
      title="Create Your Account"
      subtitle="Join NEXUS Platform to manage your finances"
      onSubmit={handleSubmit(handleFormSubmit)}
      maxWidth={500}
    >
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box sx={{ display: "flex", gap: 2, mb: 2 }}>
        <FormField
          name="firstName"
          label="First Name"
          value={formData.firstName}
          onChange={(value: string | number | boolean) =>
            handleChange("firstName", value as string)
          }
          onBlur={() => handleBlur("firstName")}
          error={!!getFieldError("firstName")}
          required
          fullWidth
          autoComplete="given-name"
        />

        <FormField
          name="lastName"
          label="Last Name"
          value={formData.lastName}
          onChange={(value: string | number | boolean) =>
            handleChange("lastName", value as string)
          }
          onBlur={() => handleBlur("lastName")}
          error={!!getFieldError("lastName")}
          required
          fullWidth
          autoComplete="family-name"
        />
      </Box>

      <FormField
        name="email"
        label="Email Address"
        type="email"
        value={formData.email}
        onChange={(value: string | number | boolean) =>
          handleChange("email", value as string)
        }
        onBlur={() => handleBlur("email")}
        error={!!getFieldError("email")}
        required
        fullWidth
        autoComplete="email"
      />

      <FormField
        name="username"
        label="Username"
        value={formData.username}
        onChange={(value: string | number | boolean) =>
          handleChange("username", value as string)
        }
        onBlur={() => handleBlur("username")}
        error={!!getFieldError("username")}
        required
        fullWidth
        autoComplete="username"
        helpText="Only letters, numbers, and underscores allowed"
      />

      <FormField
        name="password"
        label="Password"
        type="password"
        value={formData.password}
        onChange={(value: string | number | boolean) =>
          handleChange("password", value as string)
        }
        onBlur={() => handleBlur("password")}
        error={!!getFieldError("password")}
        required
        fullWidth
        autoComplete="new-password"
        helpText="Must contain uppercase, lowercase, number, and special character"
      />

      <FormField
        name="confirmPassword"
        label="Confirm Password"
        type="password"
        value={formData.confirmPassword}
        onChange={(value: string | number | boolean) =>
          handleChange("confirmPassword", value as string)
        }
        onBlur={() => handleBlur("confirmPassword")}
        error={!!getFieldError("confirmPassword")}
        required
        fullWidth
        autoComplete="new-password"
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
          Create Account
        </Button>
      </Box>

      <Box sx={{ mt: 2, textAlign: "center" }}>
        <Typography variant="body2" color="text.secondary">
          Already have an account?{" "}
          <Typography
            component="a"
            href="/login"
            variant="body2"
            color="primary"
            sx={{
              textDecoration: "none",
              "&:hover": { textDecoration: "underline" },
            }}
          >
            Sign in here
          </Typography>
        </Typography>
      </Box>
    </Form>
  );
};

export default RegisterForm;
