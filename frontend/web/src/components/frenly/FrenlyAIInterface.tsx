import React from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
} from "@mui/material";

const FrenlyAIInterface: React.FC = () => {
  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Frenly AI Interface
      </Typography>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            AI Assistant
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Interact with the Frenly AI assistant
          </Typography>

          <TextField
            fullWidth
            multiline
            rows={4}
            placeholder="Ask Frenly AI anything..."
            variant="outlined"
            sx={{ mb: 2 }}
          />

          <Button variant="contained" fullWidth>
            Send Message
          </Button>
        </CardContent>
      </Card>
    </Box>
  );
};

export default FrenlyAIInterface;
