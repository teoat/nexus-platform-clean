#!/usr/bin/env typescript
/**
 * NEXUS Platform - Radio Component
 * Accessible radio button with multiple variants
 */

import React, { forwardRef } from "react";

export interface RadioOption {
  label: string;
  value: string | number | boolean;
  disabled?: boolean;
  description?: string;
}

export interface RadioProps {
  name?: string;
  value?: string | number | boolean;
  onChange?: (value: string | number | boolean) => void;
  options?: RadioOption[];
  disabled?: boolean;
  error?: boolean;
  size?: "small" | "medium" | "large";
  variant?: "default" | "primary" | "success" | "warning" | "error";
  className?: string;
  id?: string;
  required?: boolean;
  orientation?: "vertical" | "horizontal";
}

export const Radio = forwardRef<HTMLInputElement, RadioProps>(
  (
    {
      name,
      value,
      onChange,
      options = [],
      disabled = false,
      error = false,
      size = "medium",
      variant = "default",
      className = "",
      id,
      required = false,
      orientation = "vertical",
      ...props
    },
    ref,
  ) => {
    const handleChange = (optionValue: string | number | boolean) => {
      if (disabled) return;
      onChange?.(optionValue);
    };

    const radioId =
      id || `radio-${name || Math.random().toString(36).substr(2, 9)}`;

    const sizeClasses = {
      small: "w-4 h-4",
      medium: "w-5 h-5",
      large: "w-6 h-6",
    };

    const variantClasses = {
      default: error
        ? "border-red-500 text-red-600 focus:ring-red-500"
        : "border-gray-300 text-blue-600 focus:ring-blue-500",
      primary: error
        ? "border-red-500 text-red-600 focus:ring-red-500"
        : "border-blue-300 text-blue-600 focus:ring-blue-500",
      success: error
        ? "border-red-500 text-red-600 focus:ring-red-500"
        : "border-green-300 text-green-600 focus:ring-green-500",
      warning: error
        ? "border-red-500 text-red-600 focus:ring-red-500"
        : "border-yellow-300 text-yellow-600 focus:ring-yellow-500",
      error: "border-red-300 text-red-600 focus:ring-red-500",
    };

    const orientationClasses = {
      vertical: "space-y-3",
      horizontal: "flex flex-wrap gap-6",
    };

    if (options.length === 0) {
      return null;
    }

    return (
      <div className={`${orientationClasses[orientation]} ${className}`}>
        {options.map((option, index) => {
          const optionId = `${radioId}-${index}`;
          const isChecked = value === option.value;
          const isDisabled = disabled || option.disabled;

          return (
            <div
              key={String(option.value)}
              className="flex items-start space-x-3"
            >
              <input
                ref={index === 0 ? ref : undefined}
                type="radio"
                id={optionId}
                name={name}
                value={String(option.value) as string}
                checked={isChecked}
                onChange={() => handleChange(option.value)}
                disabled={isDisabled}
                required={required}
                className={`
                  ${sizeClasses[size]}
                  rounded-full
                  border
                  ${variantClasses[variant]}
                  focus:ring-2
                  focus:ring-offset-2
                  disabled:opacity-50
                  disabled:cursor-not-allowed
                `}
                {...props}
              />
              <div className="flex-1">
                <label
                  htmlFor={optionId}
                  className={`
                    block text-sm font-medium
                    ${error ? "text-red-700 dark:text-red-400" : "text-gray-700 dark:text-gray-300"}
                    ${isDisabled ? "opacity-50" : "cursor-pointer"}
                  `}
                >
                  {option.label}
                  {required && <span className="text-red-500 ml-1">*</span>}
                </label>
                {option.description && (
                  <p
                    className={`
                      mt-1 text-sm
                      ${error ? "text-red-600 dark:text-red-400" : "text-gray-500 dark:text-gray-400"}
                      ${isDisabled ? "opacity-50" : ""}
                    `}
                  >
                    {option.description}
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    );
  },
);

Radio.displayName = "Radio";

// RadioGroup component for grouping radio buttons
export interface RadioGroupProps {
  name?: string;
  value?: string | number | boolean;
  onChange?: (value: string | number | boolean) => void;
  options?: RadioOption[];
  orientation?: "vertical" | "horizontal";
  size?: "small" | "medium" | "large";
  variant?: "default" | "primary" | "success" | "warning" | "error";
  disabled?: boolean;
  required?: boolean;
  error?: boolean;
  className?: string;
  label?: string;
  helperText?: string;
}

export const RadioGroup: React.FC<RadioGroupProps> = ({
  name,
  value,
  onChange,
  options = [],
  orientation = "vertical",
  size = "medium",
  variant = "default",
  disabled = false,
  required = false,
  error = false,
  className = "",
  label,
  helperText,
}) => {
  const orientationClasses = {
    vertical: "space-y-3",
    horizontal: "flex flex-wrap gap-6",
  };

  return (
    <fieldset className={`${className}`} disabled={disabled}>
      {label && (
        <legend className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </legend>
      )}
      <div className={orientationClasses[orientation]}>
        {options.map((option, index) => {
          const optionId = `${name || "radio"}-${index}`;
          const isChecked = value === option.value;
          const isDisabled = disabled || option.disabled;

          return (
            <div
              key={String(option.value)}
              className="flex items-start space-x-3"
            >
              <input
                type="radio"
                id={optionId}
                name={name}
                value={String(option.value) as string}
                checked={isChecked}
                onChange={() => onChange?.(option.value)}
                disabled={isDisabled}
                required={required}
                className={`
                  ${size === "small" ? "w-4 h-4" : size === "large" ? "w-6 h-6" : "w-5 h-5"}
                  rounded-full
                  border
                  ${
                    error
                      ? "border-red-500 text-red-600 focus:ring-red-500"
                      : "border-gray-300 text-blue-600 focus:ring-blue-500"
                  }
                  focus:ring-2
                  focus:ring-offset-2
                  disabled:opacity-50
                  disabled:cursor-not-allowed
                `}
              />
              <div className="flex-1">
                <label
                  htmlFor={optionId}
                  className={`
                    block text-sm font-medium
                    ${error ? "text-red-700 dark:text-red-400" : "text-gray-700 dark:text-gray-300"}
                    ${isDisabled ? "opacity-50" : "cursor-pointer"}
                  `}
                >
                  {option.label}
                </label>
                {option.description && (
                  <p
                    className={`
                      mt-1 text-sm
                      ${error ? "text-red-600 dark:text-red-400" : "text-gray-500 dark:text-gray-400"}
                      ${isDisabled ? "opacity-50" : ""}
                    `}
                  >
                    {option.description}
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
      {helperText && (
        <p
          className={`mt-1 text-sm ${error ? "text-red-600 dark:text-red-400" : "text-gray-500 dark:text-gray-400"}`}
        >
          {helperText}
        </p>
      )}
    </fieldset>
  );
};

export default Radio;
