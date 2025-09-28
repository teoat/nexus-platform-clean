import React from "react";
import {
  Button as MuiButton,
  ButtonProps as MuiButtonProps,
} from "@mui/material";

interface ButtonProps extends Omit<MuiButtonProps, "variant"> {
  variant?:
    | "contained"
    | "outlined"
    | "text"
    | "primary"
    | "secondary"
    | "danger"
    | "success";
  loading?: boolean;
}

const Button: React.FC<ButtonProps> = ({
  variant = "contained",
  loading = false,
  ...props
}) => {
  const muiVariant =
    variant === "primary"
      ? "contained"
      : variant === "secondary"
        ? "contained"
        : variant === "danger"
          ? "contained"
          : variant === "success"
            ? "contained"
            : variant;

  return (
    <MuiButton
      variant={muiVariant}
      disabled={loading || props.disabled}
      {...props}
    />
  );
};

export default Button;
