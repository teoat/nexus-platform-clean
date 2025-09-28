import React from "react";
import {
  Card as MuiCard,
  CardProps as MuiCardProps,
  CardContent,
  CardHeader,
} from "@mui/material";

interface CardProps extends MuiCardProps {
  variant?: "elevation" | "outlined";
}

const Card: React.FC<CardProps> = ({ variant = "elevation", ...props }) => {
  return <MuiCard variant={variant} {...props} />;
};

export default Card;
export { CardContent, CardHeader };
