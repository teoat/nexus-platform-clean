import React from "react";
import { Box, CircularProgress, Typography } from "@mui/material";

interface LoadingStateProps {
  message?: string;
  size?: number;
  fullScreen?: boolean;
}

const LoadingState: React.FC<LoadingStateProps> = ({
  message = "Loading...",
  size = 40,
  fullScreen = false,
}) => {
  const containerProps = fullScreen
    ? {
        position: "fixed" as const,
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 9999,
        bgcolor: "background.paper",
      }
    : {
        p: 4,
      };

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      {...containerProps}
    >
      <CircularProgress size={size} />
      <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
        {message}
      </Typography>
    </Box>
  );
};

export default LoadingState;
