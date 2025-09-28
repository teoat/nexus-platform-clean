import React from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Stepper,
  Step,
  StepLabel,
  Button,
} from "@mui/material";

const NexusPhaseDashboard: React.FC = () => {
  const steps = [
    "Phase 1: Initialization",
    "Phase 2: Configuration",
    "Phase 3: Deployment",
    "Phase 4: Monitoring",
    "Phase 5: Optimization",
  ];

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Nexus Phase Dashboard
      </Typography>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Deployment Phases
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Track the progress of your Nexus deployment
          </Typography>

          <Stepper activeStep={2} alternativeLabel>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          <Box sx={{ mt: 3 }}>
            <Button variant="contained" sx={{ mr: 1 }}>
              Next Phase
            </Button>
            <Button variant="outlined">Previous Phase</Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default NexusPhaseDashboard;
