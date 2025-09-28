/**
 * NEXUS Platform - SSOT Manager Component
 * Interface for managing SSOT aliases and context
 */

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Clear as ClearIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { useSSOT } from '@hooks/useSSOT';

interface CreateAliasForm {
  alias: string;
  canonical: string;
  description: string;
}

const SSOTManager: React.FC = () => {
  const {
    context,
    aliases,
    cacheStats,
    isLoading,
    error,
    setContext,
    createAlias,
    deleteAlias,
    refreshAliases,
    clearCache
  } = useSSOT();

  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [createForm, setCreateForm] = useState<CreateAliasForm>({
    alias: '',
    canonical: '',
    description: ''
  });
  const [contexts] = useState(['frontend', 'backend', 'frenly_ai', 'system', 'application']);

  const handleCreateAlias = async () => {
    if (!createForm.alias || !createForm.canonical) {
      return;
    }

    try {
      await createAlias(createForm.alias, createForm.canonical, createForm.description);
      setCreateDialogOpen(false);
      setCreateForm({ alias: '', canonical: '', description: '' });
    } catch (error) {
      console.error('Failed to create alias:', error);
    }
  };

  const handleDeleteAlias = async (alias: string) => {
    if (window.confirm(`Are you sure you want to delete alias '${alias}'?`)) {
      try {
        await deleteAlias(alias);
      } catch (error) {
        console.error('Failed to delete alias:', error);
      }
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        SSOT Manager
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Context Selection */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Context Management
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Current Context</InputLabel>
              <Select
                value={context}
                onChange={(e) => setContext(e.target.value)}
                label="Current Context"
              >
                {contexts.map((ctx) => (
                  <MenuItem key={ctx} value={ctx}>
                    {ctx}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Chip label={context} color="primary" />
          </Box>
        </CardContent>
      </Card>

      {/* Cache Statistics */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Cache Statistics
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <Chip 
              label={`${cacheStats.size} cached aliases`} 
              color="secondary" 
            />
            <Button
              variant="outlined"
              startIcon={<ClearIcon />}
              onClick={clearCache}
              size="small"
            >
              Clear Cache
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Aliases Management */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Aliases in Context: {context}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={refreshAliases}
                disabled={isLoading}
                size="small"
              >
                Refresh
              </Button>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setCreateDialogOpen(true)}
                size="small"
              >
                Create Alias
              </Button>
            </Box>
          </Box>

          {isLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Alias</TableCell>
                    <TableCell>Canonical</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {aliases.map((alias, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <code>@{alias.alias || alias.name}</code>
                          <Tooltip title="This alias can be used in API calls">
                            <InfoIcon fontSize="small" color="action" />
                          </Tooltip>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <code>{alias.canonical}</code>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={alias.type || 'application'} 
                          size="small" 
                          color="default"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={alias.status || 'active'} 
                          size="small" 
                          color={alias.status === 'active' ? 'success' : 'default'}
                        />
                      </TableCell>
                      <TableCell>
                        {alias.description || 'No description'}
                      </TableCell>
                      <TableCell>
                        <IconButton
                          onClick={() => handleDeleteAlias(alias.alias || alias.name)}
                          color="error"
                          size="small"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                  {aliases.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={6} align="center">
                        No aliases found in this context
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Create Alias Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Alias</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
            <TextField
              label="Alias Name"
              value={createForm.alias}
              onChange={(e) => setCreateForm(prev => ({ ...prev, alias: e.target.value }))}
              placeholder="e.g., user-management"
              helperText="Name for the alias (without @ symbol)"
              fullWidth
            />
            <TextField
              label="Canonical Endpoint"
              value={createForm.canonical}
              onChange={(e) => setCreateForm(prev => ({ ...prev, canonical: e.target.value }))}
              placeholder="e.g., /api/v1/users"
              helperText="The actual API endpoint this alias points to"
              fullWidth
            />
            <TextField
              label="Description"
              value={createForm.description}
              onChange={(e) => setCreateForm(prev => ({ ...prev, description: e.target.value }))}
              placeholder="e.g., User management endpoint for frontend"
              helperText="Optional description of what this alias is for"
              fullWidth
              multiline
              rows={2}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>
            Cancel
          </Button>
          <Button 
            onClick={handleCreateAlias} 
            variant="contained"
            disabled={!createForm.alias || !createForm.canonical}
          >
            Create Alias
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SSOTManager;
