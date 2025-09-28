import React from "react";
import { Container, Typography, Box, Paper } from "@mui/material";

const Transactions: React.FC = () => {
  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Your Transactions
        </Typography>
        <Typography variant="body1" color="text.secondary">
          View and manage all your financial transactions.
        </Typography>
      </Box>

      <Paper elevation={1} sx={{ p: 3 }}>
        <Typography variant="body1">
          Transactions content will be implemented here.
        </Typography>
      </Paper>
    </Container>
  );
};

export default Transactions;
