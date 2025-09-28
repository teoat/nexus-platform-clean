import React, { useState, useCallback } from "react";

export interface ValidationRule {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  custom?: (value: any) => string | null;
  email?: boolean;
  min?: number;
  max?: number;
}
export interface ValidationErrors {
  [key: string]: string;
}
export interface FormData {
  [key: string]: any;
}
export const useFormValidation = (
  initialData: FormData = {},
  validationRules: { [key: string]: ValidationRule } = {},
) => {
  const [formData, setFormData] = useState<FormData>(initialData);
  const [errors, setErrors] = useState<ValidationErrors>({});
  const [touched, setTouched] = useState<{ [key: string]: boolean }>({});
  const validateField = useCallback(
    (name: string, value: any): string | null => {
      const rule = validationRules[name];
      if (!rule) return null;
      if (
        rule.required &&
        (!value || (typeof value === "string" && value.trim() === ""))
      ) {
        return `${name} is required`;
      }
      if (!value || (typeof value === "string" && value.trim() === "")) {
        return null;
      }
      if (rule.email) {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(value)) {
          return "Please enter a valid email address";
        }
      }
      if (
        rule.minLength &&
        typeof value === "string" &&
        value.length < rule.minLength
      ) {
        return `${name} must be at least ${rule.minLength} characters long`;
      }
      if (
        rule.maxLength &&
        typeof value === "string" &&
        value.length > rule.maxLength
      ) {
        return `${name} must be no more than ${rule.maxLength} characters long`;
      }
      if (
        rule.pattern &&
        typeof value === "string" &&
        !rule.pattern.test(value)
      ) {
        return `${name} format is invalid`;
      }
      if (
        rule.min !== undefined &&
        typeof value === "number" &&
        value < rule.min
      ) {
        return `${name} must be at least ${rule.min}`;
      }
      if (
        rule.max !== undefined &&
        typeof value === "number" &&
        value > rule.max
      ) {
        return `${name} must be no more than ${rule.max}`;
      }
      if (rule.custom) {
        return rule.custom(value);
      }
      return null;
    },
    [validationRules],
  );
  const validateForm = useCallback((): boolean => {
    const newErrors: ValidationErrors = {};
    let isValid = true;
    Object.keys(validationRules).forEach((fieldName) => {
      const error = validateField(fieldName, formData[fieldName]);
      if (error) {
        newErrors[fieldName] = error;
        isValid = false;
      }
    });
    setErrors(newErrors);
    return isValid;
  }, [formData, validateField, validationRules]);
  const handleChange = useCallback(
    (name: string, value: any) => {
      setFormData((prev) => ({ ...prev, [name]: value }));
      if (errors[name]) {
        setErrors((prev) => {
          const newErrors = { ...prev };
          delete newErrors[name];
          return newErrors;
        });
      }
    },
    [errors],
  );
  const handleBlur = useCallback(
    (name: string) => {
      setTouched((prev) => ({ ...prev, [name]: true }));
      const error = validateField(name, formData[name]);
      if (error) {
        setErrors((prev) => ({ ...prev, [name]: error }));
      } else {
        setErrors((prev) => {
          const newErrors = { ...prev };
          delete newErrors[name];
          return newErrors;
        });
      }
    },
    [formData, validateField],
  );
  const handleSubmit = useCallback(
    (onSubmit: (data: FormData) => void) => {
      return (e: React.FormEvent) => {
        e.preventDefault();
        const allTouched: { [key: string]: boolean } = {};
        Object.keys(validationRules).forEach((fieldName) => {
          allTouched[fieldName] = true;
        });
        setTouched(allTouched);
        if (validateForm()) {
          onSubmit(formData);
        }
      };
    },
    [validateForm, formData],
  );
  const resetForm = useCallback(() => {
    setFormData(initialData);
    setErrors({});
    setTouched({});
  }, [initialData]);
  const setFieldValue = useCallback((name: string, value: any) => {
    setFormData((prev) => ({ ...prev, [name]: value }));
  }, []);
  const getFieldError = useCallback(
    (name: string): string | null => {
      return touched[name] ? errors[name] || null : null;
    },
    [errors, touched],
  );
  const isFieldTouched = useCallback(
    (name: string): boolean => {
      return touched[name] || false;
    },
    [touched],
  );
  const isFormValid = useCallback((): boolean => {
    return (
      Object.keys(errors).length === 0 &&
      Object.keys(validationRules).every((fieldName) => {
        const value = formData[fieldName];
        const rule = validationRules[fieldName];
        if (rule?.required) {
          return value && (typeof value !== "string" || value.trim() !== "");
        }
        return true;
      })
    );
  }, [errors, formData, validationRules]);
  return {
    formData,
    errors,
    touched,
    handleChange,
    handleBlur,
    handleSubmit,
    resetForm,
    setFieldValue,
    getFieldError,
    isFieldTouched,
    isFormValid,
    validateForm,
  };
};
