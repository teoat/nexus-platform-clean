import React from "react";
import { Box, Typography, Grid, Card, CardContent } from "@mui/material";

const AnalyticsDashboard: React.FC = () => {
  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Analytics Dashboard
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance Metrics
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Analytics functionality coming soon
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                User Analytics
              </Typography>
              <Typography variant="body2" color="text.secondary">
                User analytics coming soon
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AnalyticsDashboard;
