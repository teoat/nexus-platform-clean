#!/usr/bin/env typescript
/**
 * NEXUS Platform - FormField Component
 * Individual form field component with validation and error handling
 */

import React from "react";
import { Input } from "./Input";
import { Select } from "./Select";
import { Textarea } from "./Textarea";
import Checkbox from "./Checkbox";
import { RadioGroup } from "./Radio";
import Switch from "./Switch";

export interface FormFieldProps {
  name: string;
  label: string;
  type?:
    | "text"
    | "email"
    | "password"
    | "number"
    | "tel"
    | "url"
    | "textarea"
    | "select"
    | "checkbox"
    | "radio"
    | "switch"
    | "date"
    | "time"
    | "datetime-local";
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  autoComplete?: string;
  autoFocus?: boolean;
  sx?: React.CSSProperties;
  InputProps?: Record<string, unknown>;
  options?: { label: string; value: string | number }[];
  validation?: {
    required?: boolean;
    min?: number;
    max?: number;
    minLength?: number;
    maxLength?: number;
    pattern?: RegExp;
    custom?: (value: string | number) => string | null;
    message?: string;
  };
  helpText?: string;
  className?: string;
  width?: "full" | "half" | "third" | "quarter";
  value?: string | number | boolean;
  onChange?: (value: string | number | boolean) => void;
  onBlur?: () => void;
  error?: boolean;
  errorMessage?: string;
}

export const FormField: React.FC<FormFieldProps> = ({
  name,
  label,
  type = "text",
  placeholder,
  required = false,
  disabled = false,
  fullWidth = true,
  autoComplete,
  autoFocus,
  sx,
  InputProps,
  options = [],
  validation,
  helpText,
  className = "",
  width = "full",
  value,
  onChange,
  onBlur,
  error = false,
  errorMessage,
}) => {
  const fieldId = `${name}-${Math.random().toString(36).substr(2, 9)}`;

  const widthClasses = {
    full: "w-full",
    half: "w-1/2",
    third: "w-1/3",
    quarter: "w-1/4",
  };

  const renderField = () => {
    const commonProps = {
      id: fieldId,
      name,
      value: String(value || ""),
      onChange: (val: string | number | boolean) => onChange?.(val),
      onBlur: () => onBlur?.(),
      placeholder,
      disabled,
      error: error || !!errorMessage,
      fullWidth,
      autoComplete,
      autoFocus,
      sx,
      InputProps,
      className: widthClasses[width],
    };

    switch (type) {
      case "textarea":
        return <Textarea {...commonProps} label={label} />;

      case "select":
        return (
          <Select
            {...commonProps}
            options={options?.map((opt) => ({
              ...opt,
              value: String(opt.value),
            }))}
            label={label}
            onChange={(value: string | number | boolean) =>
              onChange?.(value as string | number | boolean)
            }
          />
        );

      case "checkbox":
        return (
          <Checkbox
            {...commonProps}
            checked={!!value}
            onChange={(e) => onChange?.(e.target.checked)}
            label={label}
            required={required}
          />
        );

      case "radio":
        return (
          <RadioGroup
            name={name}
            value={value}
            onChange={(val) => onChange?.(val)}
            options={options}
            disabled={disabled}
            error={error || !!errorMessage}
            label={label}
            required={required}
          />
        );

      case "switch":
        return (
          <Switch
            {...commonProps}
            checked={!!value}
            onChange={(e) => onChange?.(e.target.checked)}
            label={label}
            required={required}
          />
        );

      default:
        return <Input {...commonProps} type={type} label={label} />;
    }
  };

  const showError = error || !!errorMessage;
  const displayError = errorMessage || (error ? "This field has an error" : "");

  return (
    <div className={`${widthClasses[width]} ${className}`}>
      {type !== "checkbox" && type !== "radio" && type !== "switch" && (
        <label
          htmlFor={fieldId}
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
        >
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}

      {renderField()}

      {showError && (
        <p className="mt-1 text-sm text-red-600 dark:text-red-400">
          {displayError}
        </p>
      )}

      {helpText && !showError && (
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          {helpText}
        </p>
      )}
    </div>
  );
};

export default FormField;
