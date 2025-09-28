import React from "react";
import { Container, Typography, Box } from "@mui/material";
import AccountManagement from "../components/financial/AccountManagement";
import { useAccounts } from "../hooks/useAccounts";
// Remove this import as we'll use the Account type from AccountManagement

const Accounts: React.FC = () => {
  const { data: accounts, isLoading, error } = useAccounts();

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Your Accounts
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage and monitor all your financial accounts in one place.
        </Typography>
      </Box>

      <AccountManagement
        accounts={accounts as any[]}
        loading={isLoading}
        showActions={true}
      />
    </Container>
  );
};

export default Accounts;
