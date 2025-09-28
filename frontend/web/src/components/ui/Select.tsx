import React from "react";
import {
  FormControl,
  InputLabel,
  Select as MuiSelect,
  MenuItem,
  SelectProps as MuiSelectProps,
  FormControlProps,
} from "@mui/material";

interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps extends Omit<MuiSelectProps, "variant" | "onChange"> {
  label: string;
  value: string;
  onChange: (value: string | number | boolean) => void;
  options: SelectOption[];
  variant?: "outlined" | "filled" | "standard";
}

const Select: React.FC<SelectProps> = ({
  label,
  value,
  onChange,
  options,
  variant = "outlined",
  ...props
}) => {
  const handleChange = (e: any) => {
    onChange(e.target.value);
  };

  return (
    <FormControl variant={variant} fullWidth>
      <InputLabel>{label}</InputLabel>
      <MuiSelect value={value} onChange={handleChange} label={label} {...props}>
        {options.map((option) => (
          <MenuItem key={option.value} value={option.value}>
            {option.label}
          </MenuItem>
        ))}
      </MuiSelect>
    </FormControl>
  );
};

export { Select };
export default Select;
