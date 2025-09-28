import React from "react";
import { LinearProgress, LinearProgressProps } from "@mui/material";

interface ProgressProps extends LinearProgressProps {
  variant?: "determinate" | "indeterminate" | "buffer" | "query";
}

const Progress: React.FC<ProgressProps> = ({
  variant = "indeterminate",
  ...props
}) => {
  return <LinearProgress variant={variant} {...props} />;
};

export default Progress;
