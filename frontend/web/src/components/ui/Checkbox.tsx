import React from "react";
import {
  Checkbox as MuiCheckbox,
  CheckboxProps as MuiCheckboxProps,
} from "@mui/material";

interface CheckboxProps extends MuiCheckboxProps {
  label?: string;
}

const Checkbox: React.FC<CheckboxProps> = ({ label, ...props }) => {
  return <MuiCheckbox {...props} />;
};

export default Checkbox;
