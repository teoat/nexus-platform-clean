import React from "react";
import { Badge as MuiBadge, BadgeProps as MuiBadgeProps } from "@mui/material";

interface BadgeProps extends MuiBadgeProps {
  color?:
    | "default"
    | "primary"
    | "secondary"
    | "error"
    | "info"
    | "success"
    | "warning";
}

const Badge: React.FC<BadgeProps> = ({ color = "default", ...props }) => {
  return <MuiBadge color={color} {...props} />;
};

export default Badge;
