import React from "react";
import { Box, Typography, Grid, Card, CardContent } from "@mui/material";

const UnifiedFinanceDashboard: React.FC = () => {
  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Unified Finance Dashboard
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Financial Overview
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Unified finance functionality coming soon
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Transaction Summary
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Transaction summary coming soon
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default UnifiedFinanceDashboard;
