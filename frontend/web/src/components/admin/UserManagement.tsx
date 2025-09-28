import React from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from "@mui/material";

const UserManagement: React.FC = () => {
  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        User Management
      </Typography>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Users
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Manage system users and their permissions
          </Typography>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Role</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow>
                  <TableCell>John Doe</TableCell>
                  <TableCell>john@example.com</TableCell>
                  <TableCell>Admin</TableCell>
                  <TableCell>Active</TableCell>
                  <TableCell>
                    <Button size="small">Edit</Button>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>

          <Box sx={{ mt: 2 }}>
            <Button variant="contained">Add User</Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default UserManagement;
