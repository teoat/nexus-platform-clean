import React from "react";
import { TextField, TextFieldProps } from "@mui/material";

interface InputProps extends Omit<TextFieldProps, "variant" | "onChange"> {
  label: string;
  value: string;
  onChange: (value: string | number | boolean) => void;
  variant?: "outlined" | "filled" | "standard";
}

const Input: React.FC<InputProps> = ({
  label,
  value,
  onChange,
  variant = "outlined",
  ...props
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  };

  return (
    <TextField
      label={label}
      value={value}
      onChange={handleChange}
      variant={variant}
      fullWidth
      {...props}
    />
  );
};

export { Input };
export default Input;
