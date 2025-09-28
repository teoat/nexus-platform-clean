import React from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Switch,
  FormControlLabel,
} from "@mui/material";

const MainControlDashboard: React.FC = () => {
  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Main Control Dashboard
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Controls
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Main system control panel
              </Typography>

              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Auto-save enabled"
              />
              <br />
              <FormControlLabel
                control={<Switch />}
                label="Notifications enabled"
              />
              <br />
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Dark mode enabled"
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Common system operations
              </Typography>

              <Button variant="contained" fullWidth sx={{ mb: 1 }}>
                Restart System
              </Button>
              <Button variant="outlined" fullWidth sx={{ mb: 1 }}>
                Backup Data
              </Button>
              <Button variant="outlined" fullWidth>
                Clear Cache
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default MainControlDashboard;
