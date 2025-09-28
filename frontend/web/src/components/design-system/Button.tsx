/**
 * NEXUS Platform - Button Component
 * Unified button component with multiple variants and states
 */

import React from "react";
import { styled } from "@mui/material/styles";
import {
  Button as MuiButton,
  ButtonProps as MuiButtonProps,
  CircularProgress,
} from "@mui/material";

export interface ButtonProps extends Omit<MuiButtonProps, "variant" | "color"> {
  variant?:
    | "primary"
    | "secondary"
    | "outline"
    | "ghost"
    | "danger"
    | "success";
  size?: "small" | "medium" | "large";
  loading?: boolean;
  fullWidth?: boolean;
  icon?: React.ReactNode;
  iconPosition?: "left" | "right";
}

const StyledButton = styled(MuiButton, {
  shouldForwardProp: (prop) =>
    !["loading", "iconPosition"].includes(prop as string),
})<ButtonProps>(({
  theme,
  variant = "primary",
  size = "medium",
  loading,
  fullWidth,
}) => {
  const getVariantStyles = () => {
    switch (variant) {
      case "primary":
        return {
          backgroundColor: theme.palette.primary.main,
          color: theme.palette.primary.contrastText,
          "&:hover": {
            backgroundColor: theme.palette.primary.dark,
          },
          "&:disabled": {
            backgroundColor: theme.palette.action.disabled,
            color: theme.palette.action.disabled,
          },
        };
      case "secondary":
        return {
          backgroundColor: theme.palette.secondary.main,
          color: theme.palette.secondary.contrastText,
          "&:hover": {
            backgroundColor: theme.palette.secondary.dark,
          },
        };
      case "outline":
        return {
          backgroundColor: "transparent",
          color: theme.palette.primary.main,
          border: `1px solid ${theme.palette.primary.main}`,
          "&:hover": {
            backgroundColor: theme.palette.primary.light,
            color: theme.palette.primary.contrastText,
          },
        };
      case "ghost":
        return {
          backgroundColor: "transparent",
          color: theme.palette.text.primary,
          "&:hover": {
            backgroundColor: theme.palette.action.hover,
          },
        };
      case "danger":
        return {
          backgroundColor: theme.palette.error.main,
          color: theme.palette.error.contrastText,
          "&:hover": {
            backgroundColor: theme.palette.error.dark,
          },
        };
      case "success":
        return {
          backgroundColor: theme.palette.success.main,
          color: theme.palette.success.contrastText,
          "&:hover": {
            backgroundColor: theme.palette.success.dark,
          },
        };
      default:
        return {};
    }
  };

  const getSizeStyles = () => {
    switch (size) {
      case "small":
        return {
          padding: "4px 12px",
          fontSize: "0.75rem",
          minHeight: "32px",
        };
      case "medium":
        return {
          padding: "8px 16px",
          fontSize: "0.875rem",
          minHeight: "40px",
        };
      case "large":
        return {
          padding: "12px 24px",
          fontSize: "1rem",
          minHeight: "48px",
        };
      default:
        return {};
    }
  };

  return {
    ...getVariantStyles(),
    ...getSizeStyles(),
    borderRadius: "8px",
    textTransform: "none",
    fontWeight: 500,
    boxShadow: "none",
    width: fullWidth ? "100%" : "auto",
    position: "relative",
    "&:focus": {
      outline: `2px solid ${theme.palette.primary.light}`,
      outlineOffset: "2px",
    },
    "& .MuiButton-startIcon": {
      marginRight: "8px",
    },
    "& .MuiButton-endIcon": {
      marginLeft: "8px",
    },
  };
});

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = "primary",
  size = "medium",
  loading = false,
  disabled = false,
  icon,
  iconPosition = "left",
  startIcon,
  endIcon,
  ...props
}) => {
  const isDisabled = disabled || loading;

  const getIcon = () => {
    if (loading) {
      return <CircularProgress size={16} color="inherit" />;
    }
    if (icon) {
      return icon;
    }
    return null;
  };

  const getStartIcon = () => {
    if (loading || (icon && iconPosition === "left")) {
      return getIcon();
    }
    return startIcon;
  };

  const getEndIcon = () => {
    if (icon && iconPosition === "right") {
      return icon;
    }
    return endIcon;
  };

  return (
    <StyledButton
      size={size}
      disabled={isDisabled}
      startIcon={getStartIcon()}
      endIcon={getEndIcon()}
      {...props}
    >
      {children}
    </StyledButton>
  );
};

export default Button;
