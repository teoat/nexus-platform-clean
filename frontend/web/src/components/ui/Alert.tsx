import React from "react";
import { Alert as MuiAlert, AlertProps as MuiAlertProps } from "@mui/material";

interface AlertProps extends Omit<MuiAlertProps, "variant"> {
  variant?: "success" | "error" | "warning" | "info";
}

const Alert: React.FC<AlertProps> = ({ variant = "info", ...props }) => {
  return <MuiAlert severity={variant} {...props} />;
};

export default Alert;
