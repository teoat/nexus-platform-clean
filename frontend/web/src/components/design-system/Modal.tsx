/**
 * NEXUS Platform - Modal Component
 * Enhanced modal component with multiple variants and animations
 */

import React, { useEffect } from "react";
import { styled } from "@mui/material/styles";
import {
  Dialog,
  DialogProps,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Typography,
  Slide,
  Fade,
  Backdrop,
} from "@mui/material";
import { Close as CloseIcon } from "@mui/icons-material";

export interface ModalProps extends Omit<DialogProps, "open"> {
  open: boolean;
  onClose: () => void;
  title?: string;
  subtitle?: string;
  variant?: "default" | "fullscreen" | "centered" | "bottom-sheet";
  size?: "small" | "medium" | "large" | "xl";
  showCloseButton?: boolean;
  closeOnBackdropClick?: boolean;
  closeOnEscape?: boolean;
  actions?: React.ReactNode;
  loading?: boolean;
  persistent?: boolean;
}

const StyledDialog = styled(Dialog, {
  shouldForwardProp: (prop) => !["variant", "size"].includes(prop as string),
})<{ variant: string; size: string }>(({ theme, variant, size }) => {
  const getVariantStyles = () => {
    switch (variant) {
      case "fullscreen":
        return {
          "& .MuiDialog-paper": {
            margin: 0,
            maxHeight: "100vh",
            maxWidth: "100vw",
            borderRadius: 0,
          },
        };
      case "centered":
        return {
          "& .MuiDialog-paper": {
            margin: theme.spacing(2),
            maxHeight: "calc(100vh - 32px)",
          },
        };
      case "bottom-sheet":
        return {
          "& .MuiDialog-paper": {
            margin: 0,
            marginTop: "auto",
            maxHeight: "90vh",
            borderRadius: "16px 16px 0 0",
          },
        };
      default:
        return {};
    }
  };

  const getSizeStyles = () => {
    switch (size) {
      case "small":
        return {
          "& .MuiDialog-paper": {
            width: "400px",
            maxWidth: "90vw",
          },
        };
      case "medium":
        return {
          "& .MuiDialog-paper": {
            width: "600px",
            maxWidth: "90vw",
          },
        };
      case "large":
        return {
          "& .MuiDialog-paper": {
            width: "800px",
            maxWidth: "90vw",
          },
        };
      case "xl":
        return {
          "& .MuiDialog-paper": {
            width: "1200px",
            maxWidth: "95vw",
          },
        };
      default:
        return {};
    }
  };

  return {
    ...getVariantStyles(),
    ...getSizeStyles(),
  };
});

const StyledDialogTitle = styled(DialogTitle)(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  padding: theme.spacing(2, 3),
  borderBottom: `1px solid ${theme.palette.divider}`,
  "& .MuiTypography-root": {
    fontWeight: 600,
    fontSize: "1.25rem",
  },
}));

const StyledDialogContent = styled(DialogContent)(({ theme }) => ({
  padding: theme.spacing(3),
  "&.MuiDialogContent-root": {
    paddingTop: theme.spacing(2),
  },
}));

const StyledDialogActions = styled(DialogActions)(({ theme }) => ({
  padding: theme.spacing(2, 3),
  borderTop: `1px solid ${theme.palette.divider}`,
  gap: theme.spacing(1),
}));

const SlideTransition = React.forwardRef<
  HTMLElement,
  { children: React.ReactElement }
>(function Transition(props, ref) {
  return <Slide direction="up" ref={ref} {...props} />;
});

const FadeTransition = React.forwardRef<
  HTMLElement,
  { children: React.ReactElement }
>(function Transition(props, ref) {
  return <Fade ref={ref} {...props} />;
});

export const Modal: React.FC<ModalProps> = ({
  open,
  onClose,
  title,
  subtitle,
  variant = "default",
  size = "medium",
  showCloseButton = true,
  closeOnBackdropClick = true,
  closeOnEscape = true,
  actions,
  loading = false,
  persistent = false,
  children,
  ...props
}) => {
  useEffect(() => {
    if (open && !closeOnEscape) {
      const handleKeyDown = (event: KeyboardEvent) => {
        if (event.key === "Escape") {
          event.preventDefault();
        }
      };
      document.addEventListener("keydown", handleKeyDown);
      return () => document.removeEventListener("keydown", handleKeyDown);
    }
    return () => {}; // Return empty cleanup function when condition is false
  }, [open, closeOnEscape]);

  const getTransition = () => {
    switch (variant) {
      case "bottom-sheet":
        return SlideTransition;
      case "fullscreen":
        return FadeTransition;
      default:
        return FadeTransition;
    }
  };

  const handleBackdropClick = (_event: React.MouseEvent) => {
    if (closeOnBackdropClick && !persistent) {
      onClose();
    }
  };

  return (
    <StyledDialog
      open={open}
      onClose={onClose}
      variant={variant}
      size={size}
      TransitionComponent={getTransition()}
      BackdropComponent={Backdrop}
      BackdropProps={{
        timeout: 500,
        onClick: handleBackdropClick,
      }}
      {...props}
    >
      {title && (
        <StyledDialogTitle>
          <div>
            <Typography variant="h6" component="div">
              {title}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="text.secondary">
                {subtitle}
              </Typography>
            )}
          </div>
          {showCloseButton && (
            <IconButton
              aria-label="close"
              onClick={onClose}
              sx={{
                color: (theme) => theme.palette.grey[500],
              }}
            >
              <CloseIcon />
            </IconButton>
          )}
        </StyledDialogTitle>
      )}

      <StyledDialogContent>
        {loading ? (
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              minHeight: "200px",
            }}
          >
            Loading...
          </div>
        ) : (
          children
        )}
      </StyledDialogContent>

      {actions && <StyledDialogActions>{actions}</StyledDialogActions>}
    </StyledDialog>
  );
};

export default Modal;
