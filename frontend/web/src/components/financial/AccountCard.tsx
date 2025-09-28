import React, { useState } from "react";
import {
  Card,
  CardContent,
  Typography,
  Box,
  IconButton,
  Menu,
  MenuItem,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  Alert,
  CircularProgress,
} from "@mui/material";
import {
  MoreVert,
  Edit,
  Delete,
  AccountBalance,
  AccountBalanceWallet,
  CreditCard,
  Savings,
  TrendingUp,
  TrendingDown,
  Visibility,
  VisibilityOff,
} from "@mui/icons-material";
import { useAccountStore } from "../../store/accountStore";
import { useSnackbar } from "../../hooks/useSnackbar";
import { Account } from "../../services/accountService";

interface AccountCardProps {
  account: Account;
  onEdit?: (account: Account) => void;
  onDelete?: (accountId: string) => void;
  onView?: (account: Account) => void;
  showActions?: boolean;
  compact?: boolean;
}

const AccountCard: React.FC<AccountCardProps> = ({
  account,
  onEdit: _onEdit,
  onDelete,
  onView,
  showActions = true,
  compact = false,
}) => {
  const { updateAccount, deleteAccount, loading } = useAccountStore();
  const { showSnackbar } = useSnackbar();

  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [showBalance, setShowBalance] = useState(true);
  const [editData, setEditData] = useState({
    name: account.account_name,
    type: account.account_type,
    status: account.is_active ? "active" : "inactive",
  });

  // Handle menu open
  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
  };

  // Handle menu close
  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  // Handle edit
  const handleEdit = () => {
    setEditData({
      name: account.account_name,
      type: account.account_type,
      status: account.is_active ? "active" : "inactive",
    });
    setEditDialogOpen(true);
    handleMenuClose();
  };

  // Handle delete
  const handleDelete = () => {
    setDeleteDialogOpen(true);
    handleMenuClose();
  };

  // Handle view
  const handleView = () => {
    if (onView) {
      onView(account);
    }
    handleMenuClose();
  };

  // Handle save edit
  const handleSaveEdit = async () => {
    try {
      // Map editData to the AccountUpdate interface expected by the service
      const accountUpdateData = {
        account_name: editData.name,
        is_active: editData.status === "active",
      };
      await updateAccount(account.id, accountUpdateData);
      setEditDialogOpen(false);
      showSnackbar("Account updated successfully!", "success");
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to update account";
      showSnackbar(errorMessage, "error");
    }
  };

  // Handle confirm delete
  const handleConfirmDelete = async () => {
    try {
      await deleteAccount(account.id);
      setDeleteDialogOpen(false);
      showSnackbar("Account deleted successfully!", "success");
      if (onDelete) {
        onDelete(account.id);
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to delete account";
      showSnackbar(errorMessage, "error");
    }
  };

  // Get account type icon
  const getAccountTypeIcon = (type: string) => {
    switch (type) {
      case "checking":
        return <AccountBalanceWallet />;
      case "savings":
        return <Savings />;
      case "credit":
        return <CreditCard />;
      case "investment":
        return <TrendingUp />;
      default:
        return <AccountBalance />;
    }
  };

  // Get account type color
  const getAccountTypeColor = (type: string) => {
    switch (type) {
      case "checking":
        return "primary";
      case "savings":
        return "success";
      case "credit":
        return "warning";
      case "investment":
        return "info";
      default:
        return "default";
    }
  };

  // Format currency
  const formatCurrency = (amount: number, currency: string = "USD") => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: currency,
    }).format(amount);
  };

  // Get balance trend
  const getBalanceTrend = () => {
    // Mock trend calculation - in real app, this would be based on historical data
    const trend = Math.random() > 0.5 ? "up" : "down";
    return trend;
  };

  // Get account status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "success";
      case "inactive":
        return "warning";
      case "closed":
        return "error";
      default:
        return "default";
    }
  };

  // Calculate available credit for credit cards
  const getAvailableCredit = () => {
    if (account.account_type === "credit" && (account as any).creditLimit) {
      return (account as any).creditLimit - Math.abs(account.balance);
    }
    return null;
  };

  // Get balance display
  const getBalanceDisplay = () => {
    if (account.account_type === "credit") {
      const availableCredit = getAvailableCredit();
      return (
        <Box>
          <Typography variant="h5" color="error">
            {formatCurrency(Math.abs(account.balance), account.currency)}
          </Typography>
          {availableCredit !== null && (
            <Typography variant="body2" color="text.secondary">
              Available: {formatCurrency(availableCredit, account.currency)}
            </Typography>
          )}
        </Box>
      );
    }

    return (
      <Typography
        variant="h5"
        color={account.balance >= 0 ? "success.main" : "error.main"}
      >
        {formatCurrency(account.balance, account.currency)}
      </Typography>
    );
  };

  return (
    <>
      <Card
        sx={{
          cursor: "pointer",
          transition: "transform 0.2s, box-shadow 0.2s",
          "&:hover": {
            transform: "translateY(-2px)",
            boxShadow: 4,
          },
          height: compact ? "auto" : 200,
        }}
        onClick={() => onView && onView(account)}
      >
        <CardContent
          sx={{ height: "100%", display: "flex", flexDirection: "column" }}
        >
          {/* Header */}
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-start",
              mb: 2,
            }}
          >
            <Box
              sx={{ display: "flex", alignItems: "center", gap: 1, flex: 1 }}
            >
              {getAccountTypeIcon(account.account_type)}
              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Typography variant="h6" component="h3" noWrap>
                  {account.account_name}
                </Typography>
                <Typography variant="body2" color="text.secondary" noWrap>
                  {account.bank_name}
                </Typography>
              </Box>
            </Box>

            {showActions && (
              <IconButton size="small" onClick={handleMenuOpen} sx={{ ml: 1 }}>
                <MoreVert />
              </IconButton>
            )}
          </Box>

          {/* Account Number */}
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            •••• {account.account_number.slice(-4)}
          </Typography>

          {/* Balance */}
          <Box
            sx={{
              flex: 1,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
            }}
          >
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                mb: 1,
              }}
            >
              <Typography variant="body2" color="text.secondary">
                {account.account_type === "credit" ? "Credit Used" : "Balance"}
              </Typography>

              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowBalance(!showBalance);
                }}
              >
                {showBalance ? <Visibility /> : <VisibilityOff />}
              </IconButton>
            </Box>

            {showBalance ? (
              getBalanceDisplay()
            ) : (
              <Typography variant="h5" color="text.secondary">
                ••••••
              </Typography>
            )}
          </Box>

          {/* Interest Rate for Savings */}
          {account.account_type === "savings" &&
            (account as any).interestRate && (
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                Interest Rate: {(account as any).interestRate}%
              </Typography>
            )}

          {/* Credit Limit for Credit Cards */}
          {account.account_type === "credit" &&
            (account as any).creditLimit && (
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                Credit Limit:{" "}
                {formatCurrency((account as any).creditLimit, account.currency)}
              </Typography>
            )}

          {/* Footer */}
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mt: 2,
            }}
          >
            <Box sx={{ display: "flex", gap: 1 }}>
              <Chip
                label={account.account_type}
                color={getAccountTypeColor(account.account_type) as any}
                size="small"
              />
              <Chip
                label={account.is_active ? "active" : "inactive"}
                color={
                  getStatusColor(
                    account.is_active ? "active" : "inactive",
                  ) as any
                }
                size="small"
              />
            </Box>

            <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
              {getBalanceTrend() === "up" ? (
                <TrendingUp color="success" fontSize="small" />
              ) : (
                <TrendingDown color="error" fontSize="small" />
              )}
            </Box>
          </Box>

          {/* Last Transaction */}
          {(account as any).lastTransaction && !compact && (
            <Box sx={{ mt: 2, pt: 2, borderTop: "1px solid #e0e0e0" }}>
              <Typography variant="body2" color="text.secondary">
                Last Transaction:{" "}
                {new Date(
                  (account as any).lastTransaction,
                ).toLocaleDateString()}
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Action Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleView}>
          <Visibility sx={{ mr: 1 }} />
          View Details
        </MenuItem>
        <MenuItem onClick={handleEdit}>
          <Edit sx={{ mr: 1 }} />
          Edit Account
        </MenuItem>
        <MenuItem onClick={handleDelete} sx={{ color: "error.main" }}>
          <Delete sx={{ mr: 1 }} />
          Delete Account
        </MenuItem>
      </Menu>

      {/* Edit Dialog */}
      <Dialog
        open={editDialogOpen}
        onClose={() => setEditDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Edit Account</DialogTitle>
        <DialogContent>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 1 }}>
            <TextField
              fullWidth
              label="Account Name"
              value={editData.name}
              onChange={(e) =>
                setEditData((prev) => ({ ...prev, name: e.target.value }))
              }
            />

            <FormControl fullWidth>
              <InputLabel>Account Type</InputLabel>
              <Select
                value={editData.type}
                label="Account Type"
                onChange={(e) =>
                  setEditData((prev) => ({
                    ...prev,
                    type: e.target.value as any,
                  }))
                }
              >
                <MenuItem value="checking">Checking</MenuItem>
                <MenuItem value="savings">Savings</MenuItem>
                <MenuItem value="credit">Credit</MenuItem>
                <MenuItem value="investment">Investment</MenuItem>
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={editData.status}
                label="Status"
                onChange={(e) =>
                  setEditData((prev) => ({
                    ...prev,
                    status: e.target.value as any,
                  }))
                }
              >
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="inactive">Inactive</MenuItem>
                <MenuItem value="closed">Closed</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleSaveEdit}
            variant="contained"
            disabled={loading || !editData.name}
          >
            {loading ? <CircularProgress size={24} /> : "Save Changes"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Delete Account</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            This action cannot be undone. All transactions and data associated
            with this account will be permanently deleted.
          </Alert>
          <Typography>
            Are you sure you want to delete the account &quot;
            {account.account_name}&quot;?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleConfirmDelete}
            variant="contained"
            color="error"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : "Delete Account"}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default AccountCard;
