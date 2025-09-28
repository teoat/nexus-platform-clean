import React from "react";
import { TextField, TextFieldProps } from "@mui/material";

interface TextareaProps
  extends Omit<TextFieldProps, "variant" | "multiline" | "onChange"> {
  label: string;
  value: string;
  onChange: (value: string | number | boolean) => void;
  variant?: "outlined" | "filled" | "standard";
  rows?: number;
}

const Textarea: React.FC<TextareaProps> = ({
  label,
  value,
  onChange,
  variant = "outlined",
  rows = 4,
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
      multiline
      rows={rows}
      fullWidth
      {...props}
    />
  );
};

export { Textarea };
export default Textarea;
