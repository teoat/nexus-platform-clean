import React from "react";
import { Box, Typography, Button, Card, CardContent } from "@mui/material";

interface ErrorDisplayProps {
  title?: string;
  message?: string;
  error?: string;
  variant?: "card" | "inline";
  onRetry?: () => void;
  showRetry?: boolean;
}

const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  title = "Something went wrong",
  message,
  error,
  variant = "inline",
  onRetry,
  showRetry = true,
}) => {
  const displayMessage =
    message || error || "An error occurred while loading this content.";

  const content = (
    <>
      <Typography variant="h6" color="error" gutterBottom>
        {title}
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        {displayMessage}
      </Typography>
      {showRetry && onRetry && (
        <Button variant="outlined" onClick={onRetry}>
          Try Again
        </Button>
      )}
    </>
  );

  if (variant === "card") {
    return (
      <Card>
        <CardContent>
          <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            justifyContent="center"
            textAlign="center"
          >
            {content}
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      p={4}
      textAlign="center"
    >
      {content}
    </Box>
  );
};

export default ErrorDisplay;
