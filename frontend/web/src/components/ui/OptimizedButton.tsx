import React, { forwardRef, memo } from "react";

interface OptimizedButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "link";
  size?: "xs" | "sm" | "md" | "lg" | "xl";
  color?: "primary" | "secondary" | "success" | "warning" | "error" | "info";
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
  disabled?: boolean;
  children: React.ReactNode;
}

const ButtonComponent = forwardRef<HTMLButtonElement, OptimizedButtonProps>(
  (
    {
      variant = "primary",
      size = "md",
      color = "primary",
      loading = false,
      leftIcon,
      rightIcon,
      fullWidth = false,
      disabled = false,
      className = "",
      children,
      ...props
    },
    ref,
  ) => {
    const baseClasses =
      "inline-flex items-center justify-center font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";

    const variantClasses = {
      primary: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
      secondary: "bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500",
      outline:
        "border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus:ring-blue-500",
      ghost: "text-gray-700 hover:bg-gray-100 focus:ring-blue-500",
      link: "text-blue-600 hover:text-blue-700 underline focus:ring-blue-500",
    };

    const sizeClasses = {
      xs: "px-2 py-1 text-xs",
      sm: "px-3 py-1.5 text-sm",
      md: "px-4 py-2 text-base",
      lg: "px-6 py-3 text-lg",
      xl: "px-8 py-4 text-xl",
    };

    const buttonClasses = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${fullWidth ? "w-full" : ""} ${loading ? "cursor-wait" : ""} ${className}`;

    return (
      <button
        ref={ref}
        className={buttonClasses}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <svg
            className="animate-spin -ml-1 mr-2 h-4 w-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        )}
        {leftIcon && !loading && <span className="mr-2">{leftIcon}</span>}
        {children}
        {rightIcon && !loading && <span className="ml-2">{rightIcon}</span>}
      </button>
    );
  },
);

ButtonComponent.displayName = "OptimizedButton";

export const OptimizedButton = memo(ButtonComponent);

// Button group component
interface ButtonGroupProps {
  children: React.ReactNode;
  orientation?: "horizontal" | "vertical";
  spacing?: "sm" | "md" | "lg";
  className?: string;
}

export const ButtonGroup = memo<ButtonGroupProps>(
  ({
    children,
    orientation = "horizontal",
    spacing = "md",
    className = "",
  }) => {
    const spacingClasses = {
      sm: orientation === "horizontal" ? "space-x-1" : "space-y-1",
      md: orientation === "horizontal" ? "space-x-2" : "space-y-2",
      lg: orientation === "horizontal" ? "space-x-4" : "space-y-4",
    };

    const classes = `inline-flex ${orientation === "vertical" ? "flex-col" : "flex-row"} ${spacingClasses[spacing]} ${className}`;

    return (
      <div className={classes} role="group">
        {children}
      </div>
    );
  },
);

ButtonGroup.displayName = "ButtonGroup";

export default OptimizedButton;
