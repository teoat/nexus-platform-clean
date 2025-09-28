import React from "react";
import {
  Switch as MuiSwitch,
  SwitchProps as MuiSwitchProps,
} from "@mui/material";

interface SwitchProps extends MuiSwitchProps {
  label?: string;
}

const Switch: React.FC<SwitchProps> = ({ label, ...props }) => {
  return <MuiSwitch {...props} />;
};

export default Switch;
