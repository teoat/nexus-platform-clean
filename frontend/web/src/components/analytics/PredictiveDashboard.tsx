import React, { useState, useEffect, useCallback } from "react";
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  Alert,
  Tabs,
  Tab,
  IconButton,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from "@mui/material";
import {
  TrendingUp,
  TrendingDown,
  Warning,
  CheckCircle,
  Error,
  Refresh,
  Analytics,
  Security,
  Speed,
  Memory,
} from "@mui/icons-material";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { analyticsService } from "../../services/analyticsService";

interface DashboardMetrics {
  systemHealth: string;
  anomalyStatus: string;
  riskLevel: string;
  recentAnomalies: number;
  activeMetrics: number;
  latestRiskScore: number;
}

interface AnomalyData {
  timestamp: string;
  metric_name: string;
  value: number;
  predicted_value: number;
  anomaly_score: number;
  is_anomaly: boolean;
  confidence: number;
}

interface RiskAssessment {
  assessment_id: string;
  timestamp: string;
  risk_level: string;
  risk_score: number;
  factors: Record<string, number>;
  recommendations: string[];
  confidence: number;
}

interface TrendAnalysis {
  metric_name: string;
  trend_direction: string;
  slope: number;
  volatility: number;
  short_ma: number;
  long_ma: number;
  data_points: number;
}

const PredictiveDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [anomalies, setAnomalies] = useState<AnomalyData[]>([]);
  const [riskAssessments, setRiskAssessments] = useState<RiskAssessment[]>([]);
  const [trendAnalysis, setTrendAnalysis] = useState<TrendAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch all dashboard data in parallel
      const [metricsResponse, anomaliesResponse, riskResponse] =
        await Promise.all([
          analyticsService.getMetricsSummary(),
          analyticsService.getAnomalies(24),
          analyticsService.getRiskAssessments(5),
        ]);

      if (metricsResponse.success) {
        setMetrics({
          systemHealth:
            metricsResponse.data.combined_insights?.system_health || "unknown",
          anomalyStatus:
            metricsResponse.data.combined_insights?.anomaly_status || "unknown",
          riskLevel:
            metricsResponse.data.combined_insights?.risk_level || "unknown",
          recentAnomalies:
            metricsResponse.data.analytics_summary?.recent_anomalies || 0,
          activeMetrics:
            metricsResponse.data.analytics_summary?.active_metrics || 0,
          latestRiskScore:
            metricsResponse.data.analytics_summary?.latest_risk_score || 0,
        });
      }

      if (anomaliesResponse.success) {
        setAnomalies(anomaliesResponse.data.anomalies);
      }

      if (riskResponse.success) {
        setRiskAssessments(riskResponse.data.assessments);
      }
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? (err as Error).message : String(err);
      setError(errorMessage || "Failed to fetch dashboard data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();

    // Set up auto-refresh every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, [fetchDashboardData]);

  const getHealthColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "success";
      case "warning":
        return "warning";
      case "critical":
        return "error";
      default:
        return "default";
    }
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case "low":
        return "success";
      case "medium":
        return "warning";
      case "high":
        return "error";
      case "critical":
        return "error";
      default:
        return "default";
    }
  };

  const getAnomalyIcon = (isAnomaly: boolean) => {
    return isAnomaly ? (
      <Warning color="error" />
    ) : (
      <CheckCircle color="success" />
    );
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const prepareChartData = (anomalies: AnomalyData[]) => {
    return anomalies.slice(-20).map((anomaly) => ({
      time: new Date(anomaly.timestamp).toLocaleTimeString(),
      value: anomaly.value,
      predicted: anomaly.predicted_value,
      anomaly: anomaly.is_anomaly ? anomaly.value : null,
    }));
  };

  const prepareRiskChartData = (assessments: RiskAssessment[]) => {
    return assessments.map((assessment) => ({
      time: new Date(assessment.timestamp).toLocaleDateString(),
      score: assessment.risk_score,
      level: assessment.risk_level,
    }));
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Predictive Analytics Dashboard
        </Typography>
        <LinearProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert
          severity="error"
          action={
            <IconButton
              color="inherit"
              size="small"
              onClick={fetchDashboardData}
            >
              <Refresh />
            </IconButton>
          }
        >
          {error}
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
        }}
      >
        <Typography variant="h4" gutterBottom>
          Predictive Analytics Dashboard
        </Typography>
        <IconButton onClick={fetchDashboardData} color="primary">
          <Refresh />
        </IconButton>
      </Box>

      {/* Key Metrics Overview */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <Analytics color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">System Health</Typography>
              </Box>
              <Chip
                label={metrics?.systemHealth || "Unknown"}
                color={getHealthColor(metrics?.systemHealth || "")}
                size="small"
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <Security color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Risk Level</Typography>
              </Box>
              <Chip
                label={metrics?.riskLevel || "Unknown"}
                color={getRiskColor(metrics?.riskLevel || "")}
                size="small"
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <Warning color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Anomalies (24h)</Typography>
              </Box>
              <Typography variant="h4" color="error">
                {metrics?.recentAnomalies || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <Speed color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Active Metrics</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {metrics?.activeMetrics || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Content Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
        >
          <Tab label="Anomaly Detection" />
          <Tab label="Risk Assessment" />
          <Tab label="Trend Analysis" />
          <Tab label="System Overview" />
        </Tabs>
      </Paper>

      {/* Tab Content */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Anomaly Detection Timeline
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={prepareChartData(anomalies)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <RechartsTooltip />
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke="#8884d8"
                      strokeWidth={2}
                    />
                    <Line
                      type="monotone"
                      dataKey="predicted"
                      stroke="#82ca9d"
                      strokeWidth={2}
                    />
                    <Line
                      type="monotone"
                      dataKey="anomaly"
                      stroke="#ff7300"
                      strokeWidth={3}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Anomalies
                </Typography>
                <List>
                  {anomalies
                    .filter((a) => a.is_anomaly)
                    .slice(0, 5)
                    .map((anomaly, index) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          {getAnomalyIcon(anomaly.is_anomaly)}
                        </ListItemIcon>
                        <ListItemText
                          primary={anomaly.metric_name}
                          secondary={`Value: ${anomaly.value.toFixed(2)} | ${formatTimestamp(anomaly.timestamp)}`}
                        />
                      </ListItem>
                    ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Risk Assessment Timeline
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={prepareRiskChartData(riskAssessments)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <RechartsTooltip />
                    <Bar dataKey="score" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Latest Risk Assessment
                </Typography>
                {riskAssessments.length > 0 && (
                  <Box>
                    <Box sx={{ mb: 2 }}>
                      <Chip
                        label={riskAssessments[0].risk_level}
                        color={getRiskColor(riskAssessments[0].risk_level)}
                        size="small"
                      />
                      <Typography variant="h4" sx={{ mt: 1 }}>
                        {riskAssessments[0].risk_score.toFixed(1)}
                      </Typography>
                    </Box>

                    <Typography variant="subtitle2" gutterBottom>
                      Recommendations:
                    </Typography>
                    <List dense>
                      {riskAssessments[0].recommendations
                        .slice(0, 3)
                        .map((rec, index) => (
                          <ListItem key={index}>
                            <ListItemText primary={rec} />
                          </ListItem>
                        ))}
                    </List>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  System Metrics Trends
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Trend analysis and forecasting capabilities will be displayed
                  here. This section will show historical patterns and future
                  predictions.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  System Health Overview
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Overall system health based on predictive analytics
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={
                      metrics?.latestRiskScore
                        ? 100 - metrics.latestRiskScore
                        : 0
                    }
                    sx={{ mt: 1 }}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Analytics Engine Status
                </Typography>
                <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                  <CheckCircle color="success" sx={{ mr: 1 }} />
                  <Typography variant="body1">
                    Predictive Analytics Engine: Active
                  </Typography>
                </Box>
                <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                  <CheckCircle color="success" sx={{ mr: 1 }} />
                  <Typography variant="body1">
                    Anomaly Detection: Running
                  </Typography>
                </Box>
                <Box sx={{ display: "flex", alignItems: "center" }}>
                  <CheckCircle color="success" sx={{ mr: 1 }} />
                  <Typography variant="body1">
                    Risk Assessment: Active
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default PredictiveDashboard;
