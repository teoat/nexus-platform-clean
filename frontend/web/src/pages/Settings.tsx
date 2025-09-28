import React from "react";
import { Container, Typography, Box } from "@mui/material";

const Settings: React.FC = () => {
  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Settings
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Configure your application settings
        </Typography>
      </Box>

      <Box
        sx={{
          p: 3,
          border: "1px dashed #ccc",
          borderRadius: 1,
          textAlign: "center",
        }}
      >
        <Typography variant="h6" color="text.secondary">
          Settings functionality coming soon
        </Typography>
      </Box>
    </Container>
  );
};

export default Settings;
