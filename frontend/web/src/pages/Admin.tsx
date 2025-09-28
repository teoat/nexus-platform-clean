import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Security as SecurityIcon,
  Assessment as AssessmentIcon,
  Timeline as TimelineIcon,
  Person as PersonIcon,
  Settings as SettingsIcon,
  Download as DownloadIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { auditService, AuditLog, AuditStatistics, AuditQuery } from '../services/auditService';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`audit-tabpanel-${index}`}
      aria-labelledby={`audit-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const Admin: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [statistics, setStatistics] = useState<AuditStatistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Query state
  const [query, setQuery] = useState<AuditQuery>({
    limit: 50,
    sort_by: 'timestamp',
    sort_order: 'desc',
  });

  // Report generation state
  const [reportDialogOpen, setReportDialogOpen] = useState(false);
  const [reportTitle, setReportTitle] = useState('');
  const [reportDescription, setReportDescription] = useState('');
  const [reportFormat, setReportFormat] = useState<'json' | 'csv' | 'html' | 'excel'>('json');

  useEffect(() => {
    loadAuditData();
  }, [query]);

  const loadAuditData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [logsResult, statsResult] = await Promise.all([
        auditService.getAuditLogs(query),
        auditService.getAuditStatistics(),
      ]);

      setAuditLogs(logsResult.data);
      setStatistics(statsResult);
    } catch (err) {
      setError('Failed to load audit data');
      console.error('Error loading audit data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleQueryChange = (field: keyof AuditQuery, value: any) => {
    setQuery(prev => ({ ...prev, [field]: value }));
  };

  const handleGenerateReport = async () => {
    try {
      const report = await auditService.generateAuditReport(
        query,
        reportTitle,
        reportDescription,
        reportFormat
      );
      setReportDialogOpen(false);
      setReportTitle('');
      setReportDescription('');
      // Show success message or download link
      alert(`Report generated: ${report.file_path}`);
    } catch (err) {
      setError('Failed to generate report');
      console.error('Error generating report:', err);
    }
  };

  const getLogLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'error':
      case 'critical':
        return 'error';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      case 'debug':
        return 'default';
      default:
        return 'default';
    }
  };

  const getOperationColor = (operation: string) => {
    switch (operation.toLowerCase()) {
      case 'create':
        return 'success';
      case 'update':
        return 'info';
      case 'delete':
        return 'error';
      case 'read':
        return 'default';
      default:
        return 'default';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const renderStatisticsCards = () => {
    if (!statistics) return null;

    return (
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Operations
              </Typography>
              <Typography variant="h4">
                {statistics.total_operations.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Most Active User
              </Typography>
              <Typography variant="h6">
                {statistics.most_active_users[0]?.[0] || 'N/A'}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {statistics.most_active_users[0]?.[1] || 0} operations
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Most Common Operation
              </Typography>
              <Typography variant="h6">
                {statistics.most_common_operations[0]?.[0] || 'N/A'}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {statistics.most_common_operations[0]?.[1] || 0} times
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Security Events (7d)
              </Typography>
              <Typography variant="h4" color="error">
                {Object.values(statistics.log_level_distribution).reduce((a, b) => a + b, 0) - (statistics.log_level_distribution['info'] || 0) - (statistics.log_level_distribution['debug'] || 0)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  const renderFilters = () => (
    <Card sx={{ mb: 3 }}>
      <CardHeader
        title="Filters"
        avatar={<FilterIcon />}
      />
      <CardContent>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              label="Search"
              value={query.search_text || ''}
              onChange={(e) => handleQueryChange('search_text', e.target.value)}
              placeholder="Search in details..."
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>Operation</InputLabel>
              <Select
                value={query.operation_types?.[0] || ''}
                onChange={(e) => handleQueryChange('operation_types', e.target.value ? [e.target.value] : undefined)}
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="create">Create</MenuItem>
                <MenuItem value="read">Read</MenuItem>
                <MenuItem value="update">Update</MenuItem>
                <MenuItem value="delete">Delete</MenuItem>
                <MenuItem value="system">System</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>Log Level</InputLabel>
              <Select
                value={query.log_levels?.[0] || ''}
                onChange={(e) => handleQueryChange('log_levels', e.target.value ? [e.target.value] : undefined)}
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="debug">Debug</MenuItem>
                <MenuItem value="info">Info</MenuItem>
                <MenuItem value="warning">Warning</MenuItem>
                <MenuItem value="error">Error</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>Limit</InputLabel>
              <Select
                value={query.limit || 50}
                onChange={(e) => handleQueryChange('limit', Number(e.target.value))}
              >
                <MenuItem value={25}>25</MenuItem>
                <MenuItem value={50}>50</MenuItem>
                <MenuItem value={100}>100</MenuItem>
                <MenuItem value={500}>500</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  const renderAuditLogsTable = () => (
    <Card>
      <CardHeader
        title="Audit Logs"
        action={
          <Button
            variant="contained"
            startIcon={<DownloadIcon />}
            onClick={() => setReportDialogOpen(true)}
          >
            Generate Report
          </Button>
        }
      />
      <CardContent>
        {loading ? (
          <Box display="flex" justifyContent="center" p={3}>
            <CircularProgress />
          </Box>
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>Operation</TableCell>
                  <TableCell>Entity</TableCell>
                  <TableCell>User</TableCell>
                  <TableCell>Context</TableCell>
                  <TableCell>Level</TableCell>
                  <TableCell>Details</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {auditLogs.map((log) => (
                  <TableRow key={log.id}>
                    <TableCell>{formatTimestamp(log.timestamp)}</TableCell>
                    <TableCell>
                      <Chip
                        label={log.operation}
                        color={getOperationColor(log.operation) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{log.entity_type}</Typography>
                      <Typography variant="caption" color="textSecondary">
                        {log.entity_id}
                      </Typography>
                    </TableCell>
                    <TableCell>{log.performed_by}</TableCell>
                    <TableCell>{log.context}</TableCell>
                    <TableCell>
                      <Chip
                        label={log.log_level}
                        color={getLogLevelColor(log.log_level) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Accordion>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                          <Typography variant="body2">View Details</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                          <pre style={{ fontSize: '0.75rem', overflow: 'auto' }}>
                            {JSON.stringify(log.details, null, 2)}
                          </pre>
                        </AccordionDetails>
                      </Accordion>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </CardContent>
    </Card>
  );

  const renderStatisticsTab = () => {
    if (!statistics) return null;

    return (
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Operation Distribution" />
            <CardContent>
              <List>
                {Object.entries(statistics.operation_distribution)
                  .sort(([,a], [,b]) => b - a)
                  .slice(0, 10)
                  .map(([operation, count]) => (
                    <ListItem key={operation}>
                      <ListItemText
                        primary={operation}
                        secondary={`${count} operations`}
                      />
                    </ListItem>
                  ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Most Active Users" />
            <CardContent>
              <List>
                {statistics.most_active_users.slice(0, 10).map(([user, count]) => (
                  <ListItem key={user}>
                    <ListItemText
                      primary={user}
                      secondary={`${count} operations`}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Entity Type Distribution" />
            <CardContent>
              <List>
                {Object.entries(statistics.entity_type_distribution)
                  .sort(([,a], [,b]) => b - a)
                  .slice(0, 10)
                  .map(([entityType, count]) => (
                    <ListItem key={entityType}>
                      <ListItemText
                        primary={entityType}
                        secondary={`${count} entities`}
                      />
                    </ListItem>
                  ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Context Distribution" />
            <CardContent>
              <List>
                {Object.entries(statistics.context_distribution)
                  .sort(([,a], [,b]) => b - a)
                  .slice(0, 10)
                  .map(([context, count]) => (
                    <ListItem key={context}>
                      <ListItemText
                        primary={context}
                        secondary={`${count} operations`}
                      />
                    </ListItem>
                  ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Audit Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Comprehensive audit logging and compliance monitoring
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {renderStatisticsCards()}

        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="audit tabs">
            <Tab icon={<AssessmentIcon />} label="Logs" />
            <Tab icon={<TimelineIcon />} label="Statistics" />
            <Tab icon={<SecurityIcon />} label="Security" />
            <Tab icon={<SettingsIcon />} label="Settings" />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          {renderFilters()}
          {renderAuditLogsTable()}
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          {renderStatisticsTab()}
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" gutterBottom>
            Security Events
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Security-related audit events will be displayed here.
          </Typography>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <Typography variant="h6" gutterBottom>
            Audit Settings
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Configure audit logging settings and retention policies.
          </Typography>
        </TabPanel>

        {/* Report Generation Dialog */}
        <Dialog open={reportDialogOpen} onClose={() => setReportDialogOpen(false)} maxWidth="md" fullWidth>
          <DialogTitle>Generate Audit Report</DialogTitle>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Report Title"
              fullWidth
              value={reportTitle}
              onChange={(e) => setReportTitle(e.target.value)}
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="Report Description"
              fullWidth
              multiline
              rows={3}
              value={reportDescription}
              onChange={(e) => setReportDescription(e.target.value)}
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Report Format</InputLabel>
              <Select
                value={reportFormat}
                onChange={(e) => setReportFormat(e.target.value as any)}
              >
                <MenuItem value="json">JSON</MenuItem>
                <MenuItem value="csv">CSV</MenuItem>
                <MenuItem value="html">HTML</MenuItem>
                <MenuItem value="excel">Excel</MenuItem>
              </Select>
            </FormControl>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setReportDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleGenerateReport} variant="contained">
              Generate Report
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </LocalizationProvider>
  );
};

export default Admin;