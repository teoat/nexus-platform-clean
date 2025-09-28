import React from "react";
import { Container, Typography, Box, Grid } from "@mui/material";
import FinancialDashboard from "../components/dashboard/FinancialDashboard";
import RealTimeDashboard from "../components/dashboard/RealTimeDashboard";

const Dashboard: React.FC = () => {
  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Welcome to your NEXUS Platform dashboard
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <FinancialDashboard />
        </Grid>
        <Grid item xs={12} md={4}>
          <RealTimeDashboard />
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
