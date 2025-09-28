/**
 * NEXUS Platform - SSOT Usage Example
 * Demonstrates how to use SSOT-aware API calls
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import { useSSOT } from '@hooks/useSSOT';

const SSOTExample: React.FC = () => {
  const { get, post, context, aliases, isLoading, error } = useSSOT();
  const [users, setUsers] = useState<any[]>([]);
  const [newUser, setNewUser] = useState({ name: '', email: '' });
  const [loading, setLoading] = useState(false);

  // Example 1: Using aliases for API calls
  const loadUsers = async () => {
    setLoading(true);
    try {
      // This will resolve @user-management to the actual endpoint
      const response = await get('@user-management');
      if (response.success) {
        setUsers(Array.isArray(response.data) ? response.data : []);
      }
    } catch (error) {
      console.error('Failed to load users:', error);
    } finally {
      setLoading(false);
    }
  };

  // Example 2: Creating a new user using alias
  const createUser = async () => {
    if (!newUser.name || !newUser.email) return;
    
    setLoading(true);
    try {
      // This will resolve @user-management to the actual endpoint
      const response = await post('@user-management', newUser);
      if (response.success) {
        setNewUser({ name: '', email: '' });
        loadUsers(); // Reload users
      }
    } catch (error) {
      console.error('Failed to create user:', error);
    } finally {
      setLoading(false);
    }
  };

  // Example 3: Using Frenly AI alias
  const sendAIMessage = async () => {
    try {
      // This will resolve @frenly-ai to the actual AI endpoint
      const response = await post('@frenly-ai/chat', {
        message: 'Hello, how can you help me?',
        context: { page: 'ssot-example' }
      });
      if (response.success) {
        console.log('AI Response:', response.data);
      }
    } catch (error) {
      console.error('Failed to send AI message:', error);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        SSOT Usage Examples
      </Typography>

      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        This component demonstrates how to use SSOT aliases in API calls.
        Current context: <strong>{context}</strong>
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Available Aliases */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Available Aliases in {context} Context
          </Typography>
          {aliases.length > 0 ? (
            <List dense>
              {aliases.map((alias, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={`@${alias.alias || alias.name}`}
                    secondary={`→ ${alias.canonical} (${alias.type || 'application'})`}
                  />
                </ListItem>
              ))}
            </List>
          ) : (
            <Typography color="text.secondary">
              No aliases available in this context
            </Typography>
          )}
        </CardContent>
      </Card>

      {/* User Management Example */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            User Management (using @user-management alias)
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <TextField
              label="Name"
              value={newUser.name}
              onChange={(e) => setNewUser(prev => ({ ...prev, name: e.target.value }))}
              size="small"
            />
            <TextField
              label="Email"
              value={newUser.email}
              onChange={(e) => setNewUser(prev => ({ ...prev, email: e.target.value }))}
              size="small"
            />
            <Button
              variant="contained"
              onClick={createUser}
              disabled={loading || !newUser.name || !newUser.email}
            >
              {loading ? <CircularProgress size={20} /> : 'Create User'}
            </Button>
          </Box>

          <Button
            variant="outlined"
            onClick={loadUsers}
            disabled={loading}
            sx={{ mb: 2 }}
          >
            {loading ? <CircularProgress size={20} /> : 'Load Users'}
          </Button>

          <Divider sx={{ my: 2 }} />

          <Typography variant="subtitle2" gutterBottom>
            Users (loaded via @user-management):
          </Typography>
          {users.length > 0 ? (
            <List dense>
              {users.map((user, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={user.name || user.firstName + ' ' + user.lastName}
                    secondary={user.email}
                  />
                </ListItem>
              ))}
            </List>
          ) : (
            <Typography color="text.secondary">
              No users found
            </Typography>
          )}
        </CardContent>
      </Card>

      {/* AI Integration Example */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Frenly AI Integration (using @frenly-ai alias)
          </Typography>
          
          <Button
            variant="contained"
            onClick={sendAIMessage}
            disabled={loading}
            color="secondary"
          >
            Send AI Message
          </Button>
          
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Check the console for AI response
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default SSOTExample;
