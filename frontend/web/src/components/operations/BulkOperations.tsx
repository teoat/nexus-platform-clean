import React from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Checkbox,
  FormControlLabel,
} from "@mui/material";

const BulkOperations: React.FC = () => {
  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Bulk Operations
      </Typography>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Select Operations
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Choose operations to perform on selected items
          </Typography>

          <FormControlLabel
            control={<Checkbox />}
            label="Delete Selected Items"
          />
          <br />
          <FormControlLabel
            control={<Checkbox />}
            label="Update Selected Items"
          />
          <br />
          <FormControlLabel
            control={<Checkbox />}
            label="Export Selected Items"
          />

          <Box sx={{ mt: 2 }}>
            <Button variant="contained" sx={{ mr: 1 }}>
              Execute Operations
            </Button>
            <Button variant="outlined">Cancel</Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default BulkOperations;
