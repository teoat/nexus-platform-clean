import React from "react";
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
} from "@mui/material";

const POVSelection: React.FC = () => {
  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Point of View Selection
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                User Perspective
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Select your user perspective for the application
              </Typography>
              <Button variant="contained" fullWidth>
                Select User View
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Admin Perspective
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Select admin perspective for management features
              </Typography>
              <Button variant="outlined" fullWidth>
                Select Admin View
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default POVSelection;
