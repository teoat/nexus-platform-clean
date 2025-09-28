/**
 * NEXUS Platform - Card Component
 * Flexible card component with multiple variants and layouts
 */

import React from "react";
import { styled } from "@mui/material/styles";
import {
  Card as MuiCard,
  CardProps as MuiCardProps,
  CardContent,
  CardHeader,
  CardActions,
} from "@mui/material";

export interface CardProps extends Omit<MuiCardProps, "variant"> {
  variant?: "elevated" | "outlined" | "filled" | "glass";
  padding?: "none" | "small" | "medium" | "large";
  header?: React.ReactNode;
  actions?: React.ReactNode;
  loading?: boolean;
  hoverable?: boolean;
  clickable?: boolean;
  selected?: boolean;
}

const StyledCard = styled(MuiCard, {
  shouldForwardProp: (prop) =>
    !["variant", "padding", "hoverable", "clickable", "selected"].includes(
      prop as string,
    ),
})<CardProps>(({
  theme,
  variant = "elevated",
  padding = "medium",
  hoverable,
  clickable,
  selected,
}) => {
  const getVariantStyles = () => {
    switch (variant) {
      case "elevated":
        return {
          boxShadow: theme.shadows[2],
          border: "none",
        };
      case "outlined":
        return {
          boxShadow: "none",
          border: `1px solid ${theme.palette.divider}`,
        };
      case "filled":
        return {
          boxShadow: "none",
          border: "none",
          backgroundColor: theme.palette.background.paper,
        };
      case "glass":
        return {
          boxShadow: "none",
          backgroundColor: "rgba(255, 255, 255, 0.1)",
          backdropFilter: "blur(10px)",
          border: `1px solid ${theme.palette.divider}`,
        };
      default:
        return {};
    }
  };

  const getPaddingStyles = () => {
    switch (padding) {
      case "none":
        return { padding: 0 };
      case "small":
        return { padding: theme.spacing(1) };
      case "medium":
        return { padding: theme.spacing(2) };
      case "large":
        return { padding: theme.spacing(3) };
      default:
        return {};
    }
  };

  return {
    ...getVariantStyles(),
    ...getPaddingStyles(),
    borderRadius: "12px",
    transition: "all 0.2s ease-in-out",
    cursor: clickable ? "pointer" : "default",
    position: "relative",
    overflow: "hidden",
    ...(hoverable && {
      "&:hover": {
        transform: "translateY(-2px)",
        boxShadow: theme.shadows[8],
      },
    }),
    ...(clickable && {
      "&:hover": {
        backgroundColor: theme.palette.action.hover,
      },
      "&:active": {
        transform: "scale(0.98)",
      },
    }),
    ...(selected && {
      border: `2px solid ${theme.palette.primary.main}`,
      backgroundColor: theme.palette.primary.light,
    }),
  };
});

const CardContentStyled = styled(CardContent)(({ theme }) => ({
  padding: theme.spacing(2),
  "&:last-child": {
    paddingBottom: theme.spacing(2),
  },
}));

const CardHeaderStyled = styled(CardHeader)(({ theme }) => ({
  padding: theme.spacing(2),
  paddingBottom: theme.spacing(1),
}));

const CardActionsStyled = styled(CardActions)(({ theme }) => ({
  padding: theme.spacing(1, 2, 2),
  gap: theme.spacing(1),
}));

export const Card: React.FC<CardProps> = ({
  children,
  variant = "elevated",
  padding = "medium",
  header,
  actions,
  loading = false,
  hoverable = false,
  clickable = false,
  selected = false,
  sx,
  ...props
}) => {
  const getMuiVariant = () => {
    switch (variant) {
      case "elevated":
      case "filled":
      case "glass":
        return "outlined";
      case "outlined":
        return "outlined";
      default:
        return "outlined";
    }
  };

  return (
    <StyledCard
      variant={getMuiVariant() as "outlined"}
      padding={padding}
      hoverable={hoverable}
      clickable={clickable}
      selected={selected}
      sx={sx}
      {...props}
    >
      {header && <CardHeaderStyled>{header}</CardHeaderStyled>}
      <CardContentStyled>
        {loading ? (
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              minHeight: "100px",
            }}
          >
            Loading...
          </div>
        ) : (
          children
        )}
      </CardContentStyled>
      {actions && <CardActionsStyled>{actions}</CardActionsStyled>}
    </StyledCard>
  );
};

export default Card;
