import React, { useState, useCallback, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Chip,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Add,
  Settings,
  PlayArrow,
  Stop,
  Delete,
  Save,
  Refresh,
} from '@mui/icons-material';
import { featureService } from '../../services/featureService';

interface FeatureConfig {
  name: string;
  displayName: string;
  description: string;
  version: string;
  dependencies: string[];
  settings: Record<string, any>;
  permissions: string[];
  enabled: boolean;
  status: 'stopped' | 'starting' | 'running' | 'stopping' | 'error';
}

interface OnDemandLoaderProps {
  onFeatureLoad?: (featureName: string) => void;
  onFeatureUnload?: (featureName: string) => void;
}

const OnDemandLoader: React.FC<OnDemandLoaderProps> = ({
  onFeatureLoad,
  onFeatureUnload,
}) => {
  const [features, setFeatures] = useState<Record<string, FeatureConfig>>({});
  const [availableFeatures, setAvailableFeatures] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [configDialogOpen, setConfigDialogOpen] = useState(false);
  const [selectedConfig, setSelectedConfig] = useState<Partial<FeatureConfig> | null>(null);
  const [configLoading, setConfigLoading] = useState<Record<string, boolean>>({});
  const [configErrors, setConfigErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    loadAvailableFeatures();
    loadFeatureStates();
  }, []);

  const loadAvailableFeatures = async () => {
    try {
      setLoading(true);
      const response = await featureService.getAvailableFeatures();
      setAvailableFeatures((response as any).data.features);
    } catch (error: any) {
      setError('Failed to load available features');
    } finally {
      setLoading(false);
    }
  };

  const loadFeatureStates = async () => {
    try {
      const response = await featureService.getFeatureStates();
      const featureStates: Record<string, FeatureConfig> = {};

      for (const [name, state] of Object.entries((response as any).data.states)) {
        const stateData = state as any;
        featureStates[name] = {
          name,
          displayName: stateData.displayName || name,
          description: stateData.description || `Feature: ${name}`,
          version: stateData.version || '1.0.0',
          dependencies: stateData.dependencies || [],
          settings: stateData.settings || {},
          permissions: stateData.permissions || [],
          enabled: stateData.enabled || false,
          status: stateData.status || 'stopped',
        };
      }

      setFeatures(featureStates);
    } catch (error: any) {
      setError('Failed to load feature states');
    }
  };

  const handleConfigureFeature = useCallback((name: string) => {
    // ODF-001 TODO: Implement feature configuration loading logic
    const loadFeatureConfig = async () => {
      try {
        setConfigLoading(prev => ({ ...prev, [name]: true }));
        setConfigErrors(prev => ({ ...prev, [name]: '' }));

        const response = await featureService.getFeatureConfig(name);
        const data = response.data as any;
        setSelectedConfig({
          name,
          displayName: data.displayName || name,
          description: data.description || `Configuration for ${name}`,
          version: data.version || '1.0.0',
          dependencies: data.dependencies || [],
          settings: data.settings || {},
          permissions: data.permissions || [],
        });
        setConfigDialogOpen(true);
      } catch (error: any) {
        setConfigErrors(prev => ({
          ...prev,
          [name]: error.message || 'Failed to load configuration'
        }));
      } finally {
        setConfigLoading(prev => ({ ...prev, [name]: false }));
      }
    };

    loadFeatureConfig();
  }, []);

  const handleSaveConfiguration = useCallback(async () => {
    // ODF-002 TODO: Implement feature configuration saving
    if (!selectedConfig?.name) return;

    try {
      setConfigLoading(prev => ({ ...prev, [selectedConfig.name!]: true }));
      setConfigErrors(prev => ({ ...prev, [selectedConfig.name!]: null }));

      await featureService.updateFeatureConfig(selectedConfig.name!, {
        displayName: selectedConfig.displayName,
        description: selectedConfig.description,
        version: selectedConfig.version,
        dependencies: selectedConfig.dependencies,
        settings: selectedConfig.settings,
        permissions: selectedConfig.permissions,
      });

      // Reload feature states to reflect changes
      await loadFeatureStates();
      setConfigDialogOpen(false);
      setSelectedConfig(null);
    } catch (error: any) {
      setConfigErrors(prev => ({
        ...prev,
        [selectedConfig.name!]: error.message || 'Failed to save configuration'
      }));
    } finally {
      setConfigLoading(prev => ({ ...prev, [selectedConfig.name!]: false }));
    }
  }, [selectedConfig]);

  const handleToggleFeature = async (name: string, enabled: boolean) => {
    try {
      setConfigLoading(prev => ({ ...prev, [name]: true }));

      if (enabled) {
        await featureService.enableFeature(name);
        onFeatureLoad?.(name);
      } else {
        await featureService.disableFeature(name);
        onFeatureUnload?.(name);
      }

      await loadFeatureStates();
    } catch (error: any) {
      setConfigErrors(prev => ({
        ...prev,
        [name]: error.message || `Failed to ${enabled ? 'enable' : 'disable'} feature`
      }));
    } finally {
      setConfigLoading(prev => ({ ...prev, [name]: false }));
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'success';
      case 'starting': return 'warning';
      case 'stopping': return 'warning';
      case 'stopped': return 'default';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <PlayArrow color="success" />;
      case 'starting': return <CircularProgress size={16} />;
      case 'stopping': return <CircularProgress size={16} />;
      case 'stopped': return <Stop color="action" />;
      case 'error': return <Stop color="error" />;
      default: return <Stop color="disabled" />;
    }
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          On-Demand Feature Loader
        </Typography>
        <Button
          variant="contained"
          startIcon={<Refresh />}
          onClick={() => {
            loadAvailableFeatures();
            loadFeatureStates();
          }}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Available Features
              </Typography>
              {loading ? (
                <CircularProgress />
              ) : (
                <List>
                  {availableFeatures.map((featureName) => {
                    const feature = features[featureName];
                    return (
                      <ListItem key={featureName}>
                        <ListItemText
                          primary={feature?.displayName || featureName}
                          secondary={feature?.description || `Feature: ${featureName}`}
                        />
                        <ListItemSecondaryAction>
                          <IconButton
                            onClick={() => handleConfigureFeature(featureName)}
                            disabled={configLoading[featureName]}
                          >
                            {configLoading[featureName] ? (
                              <CircularProgress size={16} />
                            ) : (
                              <Settings />
                            )}
                          </IconButton>
                        </ListItemSecondaryAction>
                      </ListItem>
                    );
                  })}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Active Features
              </Typography>
              <List>
                {Object.entries(features).map(([name, feature]) => (
                  <ListItem key={name}>
                    <ListItemText
                      primary={
                        <Box display="flex" alignItems="center" gap={1}>
                          {getStatusIcon(feature.status)}
                          <Typography>{feature.displayName}</Typography>
                          <Chip
                            label={feature.status}
                            color={getStatusColor(feature.status) as any}
                            size="small"
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2">{feature.description}</Typography>
                          {configErrors[name] && (
                            <Alert severity="error" sx={{ mt: 1 }}>
                              {configErrors[name]}
                            </Alert>
                          )}
                        </Box>
                      }
                    />
                    <ListItemSecondaryAction>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={feature.enabled}
                            onChange={(e) => handleToggleFeature(name, e.target.checked)}
                            disabled={configLoading[name] || feature.status === 'starting' || feature.status === 'stopping'}
                          />
                        }
                        label=""
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Configuration Dialog */}
      <Dialog
        open={configDialogOpen}
        onClose={() => setConfigDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Configure Feature: {selectedConfig?.displayName}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Display Name"
                value={selectedConfig?.displayName || ''}
                onChange={(e) => setSelectedConfig(prev => ({
                  ...prev!,
                  displayName: e.target.value
                }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Version"
                value={selectedConfig?.version || ''}
                onChange={(e) => setSelectedConfig(prev => ({
                  ...prev!,
                  version: e.target.value
                }))}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Description"
                value={selectedConfig?.description || ''}
                onChange={(e) => setSelectedConfig(prev => ({
                  ...prev!,
                  description: e.target.value
                }))}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Dependencies (comma-separated)"
                value={selectedConfig?.dependencies?.join(', ') || ''}
                onChange={(e) => setSelectedConfig(prev => ({
                  ...prev!,
                  dependencies: e.target.value.split(',').map(s => s.trim()).filter(Boolean)
                }))}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Permissions (comma-separated)"
                value={selectedConfig?.permissions?.join(', ') || ''}
                onChange={(e) => setSelectedConfig(prev => ({
                  ...prev!,
                  permissions: e.target.value.split(',').map(s => s.trim()).filter(Boolean)
                }))}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfigDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleSaveConfiguration}
            variant="contained"
            disabled={configLoading[selectedConfig?.name || '']}
            startIcon={configLoading[selectedConfig?.name || ''] ? <CircularProgress size={16} /> : <Save />}
          >
            Save Configuration
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default OnDemandLoader;