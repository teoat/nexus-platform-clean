import React from "react";
import { Dialog, DialogProps as MuiDialogProps } from "@mui/material";

interface ModalProps extends Omit<MuiDialogProps, "open"> {
  open: boolean;
  onClose: () => void;
}

const Modal: React.FC<ModalProps> = ({ open, onClose, ...props }) => {
  return <Dialog open={open} onClose={onClose} {...props} />;
};

export default Modal;
