/**
 * NEXUS Platform - Chart Component
 * Unified chart component supporting multiple chart types
 */

import React, { useMemo } from "react";
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  ComposedChart,
} from "recharts";
import { Box, Typography, Paper, useTheme } from "@mui/material";
import { styled } from "@mui/material/styles";

export type ChartType =
  | "line"
  | "area"
  | "bar"
  | "pie"
  | "scatter"
  | "composed";

export interface ChartData {
  [key: string]: any;
}

export interface ChartConfig {
  dataKey: string;
  color?: string;
  strokeWidth?: number;
  fill?: string;
  type?: "monotone" | "linear" | "step" | "stepBefore" | "stepAfter";
  name?: string;
}

export interface ChartProps {
  type: ChartType;
  data: ChartData[];
  config: ChartConfig[];
  title?: string;
  subtitle?: string;
  width?: number | string;
  height?: number | string;
  showLegend?: boolean;
  showTooltip?: boolean;
  showGrid?: boolean;
  xAxisKey?: string;
  yAxisKey?: string;
  loading?: boolean;
  error?: string;
  emptyMessage?: string;
  colors?: string[];
  margin?: {
    top?: number;
    right?: number;
    bottom?: number;
    left?: number;
  };
}

const ChartContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  borderRadius: "8px",
  border: `1px solid ${theme.palette.divider}`,
}));

const ChartHeader = styled(Box)(({ theme }) => ({
  marginBottom: theme.spacing(2),
}));

const ChartContent = styled(Box)(({ theme }) => ({
  width: "100%",
  height: "100%",
  minHeight: "300px",
}));

const ErrorContainer = styled(Box)(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  minHeight: "300px",
  color: theme.palette.error.main,
}));

const LoadingContainer = styled(Box)(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  minHeight: "300px",
  color: theme.palette.text.secondary,
}));

const EmptyContainer = styled(Box)(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  minHeight: "300px",
  color: theme.palette.text.secondary,
}));

const defaultColors = [
  "#8884d8",
  "#82ca9d",
  "#ffc658",
  "#ff7300",
  "#00ff00",
  "#ff00ff",
  "#00ffff",
  "#ffff00",
];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <Paper sx={{ p: 1, border: "1px solid #ccc" }}>
        <Typography variant="body2" sx={{ fontWeight: "bold" }}>
          {label}
        </Typography>
        {payload.map((entry: any, index: number) => (
          <Typography key={index} variant="body2" sx={{ color: entry.color }}>
            {`${entry.name}: ${entry.value}`}
          </Typography>
        ))}
      </Paper>
    );
  }
  return null;
};

export const Chart: React.FC<ChartProps> = ({
  type,
  data,
  config,
  title,
  subtitle,
  width = "100%",
  height = 300,
  showLegend = true,
  showTooltip = true,
  showGrid = true,
  xAxisKey = "name",
  yAxisKey,
  loading = false,
  error,
  emptyMessage = "No data available",
  colors = defaultColors,
  margin = { top: 5, right: 30, left: 20, bottom: 5 },
}) => {
  const theme = useTheme();

  const chartConfig = useMemo(() => {
    return config.map((item, index) => ({
      ...item,
      color: item.color || colors[index % colors.length],
      strokeWidth: item.strokeWidth || 2,
      fill: item.fill || colors[index % colors.length],
    }));
  }, [config, colors]);

  const renderChart = () => {
    if (loading) {
      return (
        <LoadingContainer>
          <Typography>Loading chart...</Typography>
        </LoadingContainer>
      );
    }

    if (error) {
      return (
        <ErrorContainer>
          <Typography>{error}</Typography>
        </ErrorContainer>
      );
    }

    if (!data || data.length === 0) {
      return (
        <EmptyContainer>
          <Typography>{emptyMessage}</Typography>
        </EmptyContainer>
      );
    }

    const commonProps = {
      data,
      margin,
    };

    switch (type) {
      case "line":
        return (
          <LineChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey={xAxisKey} />
            <YAxis />
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
            {chartConfig.map((item, index) => (
              <Line
                key={index}
                type={item.type || "monotone"}
                dataKey={item.dataKey}
                stroke={item.color}
                strokeWidth={item.strokeWidth}
                name={item.name || item.dataKey}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
            ))}
          </LineChart>
        );

      case "area":
        return (
          <AreaChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey={xAxisKey} />
            <YAxis />
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
            {chartConfig.map((item, index) => (
              <Area
                key={index}
                type={item.type || "monotone"}
                dataKey={item.dataKey}
                stroke={item.color}
                fill={item.fill}
                name={item.name || item.dataKey}
              />
            ))}
          </AreaChart>
        );

      case "bar":
        return (
          <BarChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey={xAxisKey} />
            <YAxis />
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
            {chartConfig.map((item, index) => (
              <Bar
                key={index}
                dataKey={item.dataKey}
                fill={item.color}
                name={item.name || item.dataKey}
              />
            ))}
          </BarChart>
        );

      case "pie":
        return (
          <PieChart {...commonProps}>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) =>
                `${name} ${(percent * 100).toFixed(0)}%`
              }
              outerRadius={80}
              fill="#8884d8"
              dataKey={chartConfig[0]?.dataKey || "value"}
            >
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={colors[index % colors.length]}
                />
              ))}
            </Pie>
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
          </PieChart>
        );

      case "scatter":
        return (
          <ScatterChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey={xAxisKey} />
            <YAxis dataKey={yAxisKey} />
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
            {chartConfig.map((item, index) => (
              <Scatter
                key={index}
                dataKey={item.dataKey}
                fill={item.color}
                name={item.name || item.dataKey}
              />
            ))}
          </ScatterChart>
        );

      case "composed":
        return (
          <ComposedChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey={xAxisKey} />
            <YAxis />
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
            {chartConfig.map((item, index) => {
              return (
                <Line
                  key={index}
                  type={item.type || "monotone"}
                  dataKey={item.dataKey}
                  stroke={item.color}
                  strokeWidth={item.strokeWidth}
                  name={item.name || item.dataKey}
                />
              );
            })}
          </ComposedChart>
        );

      default:
        return <div>Unsupported chart type</div>;
    }
  };

  return (
    <ChartContainer elevation={0}>
      {(title || subtitle) && (
        <ChartHeader>
          {title && (
            <Typography variant="h6" gutterBottom>
              {title}
            </Typography>
          )}
          {subtitle && (
            <Typography variant="body2" color="text.secondary">
              {subtitle}
            </Typography>
          )}
        </ChartHeader>
      )}

      <ChartContent>
        <ResponsiveContainer width={width} height={height}>
          {renderChart()}
        </ResponsiveContainer>
      </ChartContent>
    </ChartContainer>
  );
};

export default Chart;
