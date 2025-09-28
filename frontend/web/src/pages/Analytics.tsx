import React from "react";
import { Container, Typography, Box } from "@mui/material";
import AnalyticsDashboard from "../components/analytics/AnalyticsDashboard";

const Analytics: React.FC = () => {
  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Analytics Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Comprehensive insights and analytics for your financial data.
        </Typography>
      </Box>

      <AnalyticsDashboard />
    </Container>
  );
};

export default Analytics;
