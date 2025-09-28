import React from "react";
import { Box, BoxProps, Typography, Paper } from "@mui/material";

interface FormProps extends BoxProps {
  onSubmit?: (e: React.FormEvent) => void;
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  maxWidth?: number;
}

const Form: React.FC<FormProps> = ({
  onSubmit,
  children,
  title,
  subtitle,
  maxWidth = 400,
  ...props
}) => {
  return (
    <Paper elevation={3} sx={{ p: 4, maxWidth, mx: "auto" }}>
      {title && (
        <Typography variant="h4" component="h1" gutterBottom align="center">
          {title}
        </Typography>
      )}
      {subtitle && (
        <Typography
          variant="body1"
          color="text.secondary"
          align="center"
          sx={{ mb: 3 }}
        >
          {subtitle}
        </Typography>
      )}
      <Box component="form" onSubmit={onSubmit} {...props}>
        {children}
      </Box>
    </Paper>
  );
};

export default Form;
