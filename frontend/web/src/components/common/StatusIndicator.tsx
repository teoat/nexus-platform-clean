/**
 * NEXUS Platform - StatusIndicator Component
 * Visual status indicator with multiple variants and animations
 */

import React from "react";
import {
  Box,
  Typography,
  Chip,
  LinearProgress,
  CircularProgress,
} from "@mui/material";
import { styled } from "@mui/material/styles";
import {
  CheckCircle,
  Error,
  Warning,
  Info,
  Pending,
  Schedule,
} from "@mui/icons-material";

export type StatusType =
  | "success"
  | "error"
  | "warning"
  | "info"
  | "pending"
  | "loading"
  | "scheduled";

export interface StatusIndicatorProps {
  status: StatusType;
  label?: string;
  variant?: "chip" | "dot" | "progress" | "icon";
  size?: "small" | "medium" | "large";
  showLabel?: boolean;
  animated?: boolean;
  progress?: number;
  message?: string;
  timestamp?: string;
}

const StatusContainer = styled(Box)(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  gap: theme.spacing(1),
}));

const StatusDot = styled(Box, {
  shouldForwardProp: (prop) =>
    !["status", "size", "animated"].includes(prop as string),
})<{
  status: StatusType;
  size: "small" | "medium" | "large";
  animated: boolean;
}>(({ theme, status, size, animated }) => {
  const getSize = () => {
    switch (size) {
      case "small":
        return { width: 8, height: 8 };
      case "medium":
        return { width: 12, height: 12 };
      case "large":
        return { width: 16, height: 16 };
      default:
        return { width: 12, height: 12 };
    }
  };

  const getColor = () => {
    switch (status) {
      case "success":
        return theme.palette.success.main;
      case "error":
        return theme.palette.error.main;
      case "warning":
        return theme.palette.warning.main;
      case "info":
        return theme.palette.info.main;
      case "pending":
        return theme.palette.grey[500];
      case "loading":
        return theme.palette.primary.main;
      case "scheduled":
        return theme.palette.secondary.main;
      default:
        return theme.palette.grey[500];
    }
  };

  return {
    ...getSize(),
    borderRadius: "50%",
    backgroundColor: getColor(),
    ...(animated && {
      animation:
        status === "loading"
          ? "pulse 1.5s ease-in-out infinite"
          : status === "pending"
            ? "blink 2s ease-in-out infinite"
            : "none",
    }),
    "@keyframes pulse": {
      "0%": {
        opacity: 1,
        transform: "scale(1)",
      },
      "50%": {
        opacity: 0.5,
        transform: "scale(1.1)",
      },
      "100%": {
        opacity: 1,
        transform: "scale(1)",
      },
    },
    "@keyframes blink": {
      "0%, 50%": {
        opacity: 1,
      },
      "51%, 100%": {
        opacity: 0.3,
      },
    },
  };
});

const StatusChip = styled(Chip, {
  shouldForwardProp: (prop) => !["status", "size"].includes(prop as string),
})<{ status: StatusType; size: "small" | "medium" | "large" }>(({
  theme,
  status,
  size,
}) => {
  const getColor = () => {
    switch (status) {
      case "success":
        return {
          color: theme.palette.success.contrastText,
          backgroundColor: theme.palette.success.main,
        };
      case "error":
        return {
          color: theme.palette.error.contrastText,
          backgroundColor: theme.palette.error.main,
        };
      case "warning":
        return {
          color: theme.palette.warning.contrastText,
          backgroundColor: theme.palette.warning.main,
        };
      case "info":
        return {
          color: theme.palette.info.contrastText,
          backgroundColor: theme.palette.info.main,
        };
      case "pending":
        return {
          color: theme.palette.grey[700],
          backgroundColor: theme.palette.grey[300],
        };
      case "loading":
        return {
          color: theme.palette.primary.contrastText,
          backgroundColor: theme.palette.primary.main,
        };
      case "scheduled":
        return {
          color: theme.palette.secondary.contrastText,
          backgroundColor: theme.palette.secondary.main,
        };
      default:
        return {
          color: theme.palette.grey[700],
          backgroundColor: theme.palette.grey[300],
        };
    }
  };

  const getSize = (): { height: number; fontSize: string } => {
    switch (size as "small" | "medium" | "large") {
      case "small":
        return { height: 24, fontSize: "0.75rem" };
      case "medium":
        return { height: 32, fontSize: "0.875rem" };
      case "large":
        return { height: 40, fontSize: "1rem" };
      default:
        return { height: 32, fontSize: "0.875rem" };
    }
  };

  return {
    ...getColor(),
    ...getSize(),
    fontWeight: 500,
    borderRadius: "16px",
  };
});

const StatusIcon = styled(Box, {
  shouldForwardProp: (prop) => !["status", "size"].includes(prop as string),
})<{ status: StatusType; size: "small" | "medium" | "large" }>(({
  theme,
  status,
  size,
}) => {
  const getSize = () => {
    switch (size) {
      case "small":
        return { fontSize: "16px" };
      case "medium":
        return { fontSize: "20px" };
      case "large":
        return { fontSize: "24px" };
      default:
        return { fontSize: "20px" };
    }
  };

  const getColor = () => {
    switch (status) {
      case "success":
        return theme.palette.success.main;
      case "error":
        return theme.palette.error.main;
      case "warning":
        return theme.palette.warning.main;
      case "info":
        return theme.palette.info.main;
      case "pending":
        return theme.palette.grey[500];
      case "loading":
        return theme.palette.primary.main;
      case "scheduled":
        return theme.palette.secondary.main;
      default:
        return theme.palette.grey[500];
    }
  };

  return {
    ...getSize(),
    color: getColor(),
    display: "flex",
    alignItems: "center",
  };
});

const getStatusIcon = (status: StatusType) => {
  switch (status) {
    case "success":
      return <CheckCircle />;
    case "error":
      return <Error />;
    case "warning":
      return <Warning />;
    case "info":
      return <Info />;
    case "pending":
      return <Pending />;
    case "loading":
      return <CircularProgress size={16} />;
    case "scheduled":
      return <Schedule />;
    default:
      return <Info />;
  }
};

const getStatusLabel = (status: StatusType) => {
  switch (status) {
    case "success":
      return "Success";
    case "error":
      return "Error";
    case "warning":
      return "Warning";
    case "info":
      return "Info";
    case "pending":
      return "Pending";
    case "loading":
      return "Loading";
    case "scheduled":
      return "Scheduled";
    default:
      return "Unknown";
  }
};

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  label,
  variant = "chip",
  size = "medium" as "small" | "medium" | "large",
  showLabel = true,
  animated = false,
  progress,
  message,
  timestamp,
}) => {
  const displayLabel = label || getStatusLabel(status);

  const renderIndicator = () => {
    switch (variant) {
      case "dot":
        return <StatusDot status={status} size={size} animated={animated} />;

      case "chip":
        return (
          <StatusChip
            status={status}
            size={size === "large" ? "medium" : size}
            label={displayLabel}
            icon={variant === "chip" ? getStatusIcon(status) : undefined}
          />
        );

      case "icon":
        return (
          <StatusIcon status={status} size={size}>
            {getStatusIcon(status)}
          </StatusIcon>
        );

      case "progress":
        return (
          <Box sx={{ width: "100%", minWidth: 200 }}>
            <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
              <StatusDot status={status} size="small" animated={animated} />
              <Typography variant="body2" sx={{ ml: 1 }}>
                {displayLabel}
              </Typography>
              {progress !== undefined && (
                <Typography variant="body2" sx={{ ml: "auto" }}>
                  {Math.round(progress)}%
                </Typography>
              )}
            </Box>
            <LinearProgress
              variant={progress !== undefined ? "determinate" : "indeterminate"}
              value={progress}
              sx={{
                height: 6,
                borderRadius: 3,
                backgroundColor: "rgba(0, 0, 0, 0.1)",
                "& .MuiLinearProgress-bar": {
                  borderRadius: 3,
                },
              }}
            />
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <StatusContainer>
      {renderIndicator()}
      {showLabel && variant !== "chip" && (
        <Typography variant="body2" color="text.primary">
          {displayLabel}
        </Typography>
      )}
      {message && (
        <Typography variant="caption" color="text.secondary">
          {message}
        </Typography>
      )}
      {timestamp && (
        <Typography variant="caption" color="text.secondary">
          {timestamp}
        </Typography>
      )}
    </StatusContainer>
  );
};

export default StatusIndicator;
