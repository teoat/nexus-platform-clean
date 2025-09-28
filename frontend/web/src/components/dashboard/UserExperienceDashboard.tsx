import React from "react";
import { Box, Typography, Grid, Card, CardContent } from "@mui/material";

const UserExperienceDashboard: React.FC = () => {
  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        User Experience Dashboard
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                User Analytics
              </Typography>
              <Typography variant="body2" color="text.secondary">
                User experience functionality coming soon
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance Metrics
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Performance metrics coming soon
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default UserExperienceDashboard;
