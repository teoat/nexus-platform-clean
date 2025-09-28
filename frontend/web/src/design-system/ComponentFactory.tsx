/**
 * Component Factory for NEXUS Platform
 * Factory pattern for creating consistent components
 */

import React from "react";
import { designTokens } from "./DesignTokens";

export interface ComponentConfig {
  variant?: "primary" | "secondary" | "success" | "error" | "warning";
  size?: "small" | "medium" | "large";
  disabled?: boolean;
  fullWidth?: boolean;
}

export class ComponentFactory {
  static createButton(config: ComponentConfig = {}) {
    const {
      variant = "primary",
      size = "medium",
      disabled = false,
      fullWidth = false,
    } = config;

    return {
      variant,
      size,
      disabled,
      fullWidth,
      style: {
        backgroundColor: designTokens.colors[variant][500],
        color: "white",
        padding:
          size === "small"
            ? designTokens.spacing.sm
            : size === "large"
              ? designTokens.spacing.lg
              : designTokens.spacing.md,
        borderRadius: designTokens.borderRadius.md,
        width: fullWidth ? "100%" : "auto",
        opacity: disabled ? 0.6 : 1,
        cursor: disabled ? "not-allowed" : "pointer",
      },
    };
  }

  static createCard(config: ComponentConfig = {}) {
    const { variant = "primary", size = "medium" } = config;

    return {
      variant,
      size,
      style: {
        padding:
          size === "small"
            ? designTokens.spacing.md
            : size === "large"
              ? designTokens.spacing.xl
              : designTokens.spacing.lg,
        borderRadius: designTokens.borderRadius.lg,
        boxShadow: designTokens.shadows.md,
        backgroundColor: "white",
        border: `1px solid ${designTokens.colors[variant][200]}`,
      },
    };
  }

  static createInput(config: ComponentConfig = {}) {
    const {
      variant = "primary",
      size = "medium",
      disabled = false,
      fullWidth = false,
    } = config;

    return {
      variant,
      size,
      disabled,
      fullWidth,
      style: {
        padding:
          size === "small"
            ? designTokens.spacing.sm
            : size === "large"
              ? designTokens.spacing.lg
              : designTokens.spacing.md,
        borderRadius: designTokens.borderRadius.md,
        border: `1px solid ${designTokens.colors[variant][300]}`,
        width: fullWidth ? "100%" : "auto",
        opacity: disabled ? 0.6 : 1,
        cursor: disabled ? "not-allowed" : "text",
        fontSize:
          designTokens.typography.fontSize[
            size === "small" ? "sm" : size === "large" ? "lg" : "md"
          ],
      },
    };
  }
}

// Size variants for components
export const sizeVariants = {
  small: {
    padding: designTokens.spacing.sm,
    fontSize: designTokens.typography.fontSize.sm,
    minHeight: "32px",
  },
  medium: {
    padding: designTokens.spacing.md,
    fontSize: designTokens.typography.fontSize.md,
    minHeight: "40px",
  },
  large: {
    padding: designTokens.spacing.lg,
    fontSize: designTokens.typography.fontSize.lg,
    minHeight: "48px",
  },
};

// Color variants for components
export const colorVariants = {
  primary: {
    backgroundColor: designTokens.colors.primary[500],
    color: "#ffffff",
    "&:hover": {
      backgroundColor: designTokens.colors.primary[600],
    },
  },
  secondary: {
    backgroundColor: designTokens.colors.secondary[500],
    color: "#ffffff",
    "&:hover": {
      backgroundColor: designTokens.colors.secondary[600],
    },
  },
  success: {
    backgroundColor: designTokens.colors.success[500],
    color: "#ffffff",
    "&:hover": {
      backgroundColor: designTokens.colors.success[600],
    },
  },
  warning: {
    backgroundColor: designTokens.colors.warning[500],
    color: "#ffffff",
    "&:hover": {
      backgroundColor: designTokens.colors.warning[600],
    },
  },
  error: {
    backgroundColor: designTokens.colors.error[500],
    color: "#ffffff",
    "&:hover": {
      backgroundColor: designTokens.colors.error[600],
    },
  },
};

// Generate CSS classes based on props
export const generateClasses = (baseClass: string, props: any) => {
  const classes = [baseClass];

  if (props.size) {
    classes.push(`${baseClass}--${props.size}`);
  }

  if (props.variant) {
    classes.push(`${baseClass}--${props.variant}`);
  }

  if (props.disabled) {
    classes.push(`${baseClass}--disabled`);
  }

  return classes.join(" ");
};

// Create optimized component with memo and forwardRef
export const createOptimizedComponent = <P extends object>(
  Component: React.ComponentType<P>,
  displayName?: string,
) => {
  const OptimizedComponent = React.memo(
    React.forwardRef<any, P>((props, ref) => {
      return React.createElement(Component, { ...props, ref } as any);
    }),
  );

  if (displayName) {
    OptimizedComponent.displayName = displayName;
  }

  return OptimizedComponent;
};

export default ComponentFactory;
