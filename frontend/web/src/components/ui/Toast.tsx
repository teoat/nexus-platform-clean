import React from "react";
import { Snackbar, Alert, AlertProps } from "@mui/material";

interface ToastProps {
  open: boolean;
  onClose: () => void;
  message: string;
  severity?: "success" | "error" | "warning" | "info";
  duration?: number;
}

const Toast: React.FC<ToastProps> = ({
  open,
  onClose,
  message,
  severity = "info",
  duration = 6000,
}) => {
  return (
    <Snackbar
      open={open}
      autoHideDuration={duration}
      onClose={onClose}
      anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
    >
      <Alert onClose={onClose} severity={severity} sx={{ width: "100%" }}>
        {message}
      </Alert>
    </Snackbar>
  );
};

export default Toast;
