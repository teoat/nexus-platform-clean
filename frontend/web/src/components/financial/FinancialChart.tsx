import React, { memo, useMemo, useCallback } from "react";
import { Card, CardHeader, CardContent } from "@/components/ui";
import { useTranslationHook } from "../../contexts/I18nContext";

interface DataPoint {
  date: string;
  value: number;
  category?: string;
  label?: string;
}

interface FinancialChartProps {
  title: string;
  data: DataPoint[];
  type: "line" | "bar" | "pie" | "area" | "donut";
  height?: number;
  color?: string;
  showLegend?: boolean;
  showGrid?: boolean;
  formatValue?: (value: number) => string;
  onDataPointClick?: (dataPoint: DataPoint) => void;
  loading?: boolean;
}

const FinancialChart: React.FC<FinancialChartProps> = memo(
  ({
    title,
    data,
    type,
    height = 300,
    color = "#3b82f6",
    showLegend = false,
    showGrid = true,
    formatValue,
    onDataPointClick,
    loading = false,
  }) => {
    const { t } = useTranslationHook();
    const formatCurrency = (amount: number) =>
      new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
      }).format(amount);

    // Default value formatter
    const defaultFormatValue = useCallback(
      (value: number) => {
        return formatCurrency(value);
      },
      [formatCurrency],
    );

    const valueFormatter = formatValue || defaultFormatValue;

    // Calculate chart dimensions
    const chartDimensions = useMemo(() => {
      const padding = 40;
      const width = 600; // Fixed width for now
      const chartWidth = width - padding * 2;
      const chartHeight = height - padding * 2;

      return { width, height, chartWidth, chartHeight, padding };
    }, [height]);

    // Process data for different chart types
    const processedData = useMemo(() => {
      if (type === "pie" || type === "donut") {
        // Group data by category for pie charts
        const categoryTotals: { [key: string]: number } = {};
        data.forEach((point) => {
          const category = point.category || "Uncategorized";
          categoryTotals[category] =
            (categoryTotals[category] || 0) + point.value;
        });

        return Object.entries(categoryTotals).map(
          ([category, value], index) => ({
            category,
            value,
            color: `hsl(${(index * 137.5) % 360}, 70%, 50%)`, // Golden angle approximation
            percentage:
              data.length > 0
                ? (value / data.reduce((sum, d) => sum + d.value, 0)) * 100
                : 0,
          }),
        );
      }

      return data.sort(
        (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime(),
      );
    }, [data, type]);

    // Generate SVG path for line/area charts
    const generatePath = useCallback(
      (points: DataPoint[], curved: boolean = false) => {
        if (points.length === 0) return "";

        const { chartWidth, chartHeight, padding } = chartDimensions;
        const minValue = Math.min(...points.map((p) => p.value));
        const maxValue = Math.max(...points.map((p) => p.value));
        const valueRange = maxValue - minValue || 1;

        const xStep = chartWidth / (points.length - 1 || 1);

        const pathPoints = points.map((point, index) => {
          const x = padding + index * xStep;
          const y =
            padding +
            chartHeight -
            ((point.value - minValue) / valueRange) * chartHeight;
          return `${index === 0 ? "M" : "L"} ${x} ${y}`;
        });

        if (curved && points.length > 2) {
          // Simple curve implementation
          const curvedPoints: string[] = [];
          for (let i = 0; i < pathPoints.length - 1; i++) {
            const current = pathPoints[i];
            const next = pathPoints[i + 1];
            const controlX =
              (parseFloat(current.split(" ")[1]) +
                parseFloat(next.split(" ")[1])) /
              2;
            curvedPoints.push(
              `${current} Q ${controlX} ${current.split(" ")[2]} ${next}`,
            );
          }
          return curvedPoints.join(" ");
        }

        return pathPoints.join(" ");
      },
      [chartDimensions],
    );

    // Generate bars for bar chart
    const generateBars = useCallback(
      (points: DataPoint[]) => {
        const { chartWidth, chartHeight, padding } = chartDimensions;
        const minValue = Math.min(...points.map((p) => p.value));
        const maxValue = Math.max(...points.map((p) => p.value));
        const valueRange = maxValue - minValue || 1;

        const barWidth = (chartWidth / points.length) * 0.8;
        const barSpacing = (chartWidth / points.length) * 0.2;

        return points.map((point, index) => {
          const x = padding + index * (barWidth + barSpacing) + barSpacing / 2;
          const barHeight =
            ((point.value - minValue) / valueRange) * chartHeight;
          const y = padding + chartHeight - barHeight;

          return {
            x,
            y,
            width: barWidth,
            height: barHeight,
            value: point.value,
            label: point.label || point.date,
            category: point.category,
          };
        });
      },
      [chartDimensions],
    );

    // Generate pie chart slices
    const generatePieSlices = useCallback(
      (data: any[]) => {
        const { chartWidth, chartHeight, padding } = chartDimensions;
        const centerX = chartWidth / 2 + padding;
        const centerY = chartHeight / 2 + padding;
        const radius = (Math.min(chartWidth, chartHeight) / 2) * 0.8;

        let currentAngle = -Math.PI / 2; // Start at top

        return data.map((item, index) => {
          const angle = (item.percentage / 100) * 2 * Math.PI;
          const startAngle = currentAngle;
          const endAngle = currentAngle + angle;

          const x1 = centerX + radius * Math.cos(startAngle);
          const y1 = centerY + radius * Math.sin(startAngle);
          const x2 = centerX + radius * Math.cos(endAngle);
          const y2 = centerY + radius * Math.sin(endAngle);

          const largeArcFlag = angle > Math.PI ? 1 : 0;

          const pathData = [
            `M ${centerX} ${centerY}`,
            `L ${x1} ${y1}`,
            `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}`,
            "Z",
          ].join(" ");

          currentAngle = endAngle;

          return {
            pathData,
            color: item.color,
            value: item.value,
            percentage: item.percentage,
            category: item.category,
          };
        });
      },
      [chartDimensions],
    );

    const handleDataPointClick = useCallback(
      (dataPoint: any) => {
        onDataPointClick?.(dataPoint);
      },
      [onDataPointClick],
    );

    if (loading) {
      return (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-medium">{title}</h3>
          </CardHeader>
          <CardContent>
            <div
              className="flex items-center justify-center"
              style={{ height }}
            >
              <div className="text-center text-gray-500 dark:text-gray-400">
                {t("loading.chart")}
              </div>
            </div>
          </CardContent>
        </Card>
      );
    }

    return (
      <Card>
        <CardHeader>
          <h3 className="text-lg font-medium">{title}</h3>
        </CardHeader>
        <CardContent>
          <div className="w-full overflow-x-auto">
            <svg
              width={chartDimensions.width}
              height={chartDimensions.height}
              viewBox={`0 0 ${chartDimensions.width} ${chartDimensions.height}`}
              className="w-full h-auto"
            >
              {/* Grid lines */}
              {showGrid && type !== "pie" && type !== "donut" && (
                <defs>
                  <pattern
                    id="grid"
                    width="20"
                    height="20"
                    patternUnits="userSpaceOnUse"
                  >
                    <path
                      d={`M 20 0 L 0 0 0 20`}
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="0.5"
                      className="text-gray-200 dark:text-gray-700"
                    />
                  </pattern>
                </defs>
              )}

              {/* Chart content based on type */}
              {type === "line" && (
                <>
                  {showGrid && (
                    <rect
                      width={chartDimensions.chartWidth}
                      height={chartDimensions.chartHeight}
                      x={chartDimensions.padding}
                      y={chartDimensions.padding}
                      fill="url(#grid)"
                    />
                  )}
                  <path
                    d={generatePath(processedData as DataPoint[], true)}
                    fill="none"
                    stroke={color}
                    strokeWidth="2"
                    className="drop-shadow-sm"
                  />
                  {/* Data points */}
                  {(processedData as DataPoint[]).map((point, index) => {
                    const { chartWidth, chartHeight, padding } =
                      chartDimensions;
                    const minValue = Math.min(
                      ...(processedData as DataPoint[]).map((p) => p.value),
                    );
                    const maxValue = Math.max(
                      ...(processedData as DataPoint[]).map((p) => p.value),
                    );
                    const valueRange = maxValue - minValue || 1;

                    const x =
                      padding +
                      (index * chartWidth) /
                        ((processedData as DataPoint[]).length - 1 || 1);
                    const y =
                      padding +
                      chartHeight -
                      ((point.value - minValue) / valueRange) * chartHeight;

                    return (
                      <circle
                        key={index}
                        cx={x}
                        cy={y}
                        r="4"
                        fill={color}
                        className="cursor-pointer hover:r-6 transition-all"
                        onClick={() => handleDataPointClick(point)}
                      />
                    );
                  })}
                </>
              )}

              {type === "bar" && (
                <>
                  {showGrid && (
                    <rect
                      width={chartDimensions.chartWidth}
                      height={chartDimensions.chartHeight}
                      x={chartDimensions.padding}
                      y={chartDimensions.padding}
                      fill="url(#grid)"
                    />
                  )}
                  {generateBars(processedData as DataPoint[]).map(
                    (bar, index) => (
                      <rect
                        key={index}
                        x={bar.x}
                        y={bar.y}
                        width={bar.width}
                        height={bar.height}
                        fill={color}
                        className="cursor-pointer hover:opacity-80 transition-opacity"
                        onClick={() => handleDataPointClick(bar)}
                      />
                    ),
                  )}
                </>
              )}

              {(type === "pie" || type === "donut") && (
                <g>
                  {generatePieSlices(processedData as any[]).map(
                    (slice, index) => (
                      <path
                        key={index}
                        d={slice.pathData}
                        fill={slice.color}
                        className="cursor-pointer hover:opacity-80 transition-opacity"
                        onClick={() => handleDataPointClick(slice)}
                      />
                    ),
                  )}
                  {type === "donut" && (
                    <circle
                      cx={
                        chartDimensions.chartWidth / 2 + chartDimensions.padding
                      }
                      cy={
                        chartDimensions.chartHeight / 2 +
                        chartDimensions.padding
                      }
                      r={
                        (Math.min(
                          chartDimensions.chartWidth,
                          chartDimensions.chartHeight,
                        ) /
                          2) *
                        0.4
                      }
                      fill="white"
                    />
                  )}
                </g>
              )}

              {type === "area" && (
                <>
                  {showGrid && (
                    <rect
                      width={chartDimensions.chartWidth}
                      height={chartDimensions.chartHeight}
                      x={chartDimensions.padding}
                      y={chartDimensions.padding}
                      fill="url(#grid)"
                    />
                  )}
                  <path
                    d={`${generatePath(processedData as DataPoint[], true)} L ${
                      chartDimensions.padding + chartDimensions.chartWidth
                    } ${chartDimensions.padding + chartDimensions.chartHeight} L ${
                      chartDimensions.padding
                    } ${chartDimensions.padding + chartDimensions.chartHeight} Z`}
                    fill={color}
                    fillOpacity="0.3"
                    stroke={color}
                    strokeWidth="2"
                    className="drop-shadow-sm"
                  />
                </>
              )}

              {/* Axes and labels */}
              {type !== "pie" && type !== "donut" && (
                <>
                  {/* X-axis */}
                  <line
                    x1={chartDimensions.padding}
                    y1={chartDimensions.padding + chartDimensions.chartHeight}
                    x2={chartDimensions.padding + chartDimensions.chartWidth}
                    y2={chartDimensions.padding + chartDimensions.chartHeight}
                    stroke="currentColor"
                    strokeWidth="1"
                    className="text-gray-400"
                  />
                  {/* Y-axis */}
                  <line
                    x1={chartDimensions.padding}
                    y1={chartDimensions.padding}
                    x2={chartDimensions.padding}
                    y2={chartDimensions.padding + chartDimensions.chartHeight}
                    stroke="currentColor"
                    strokeWidth="1"
                    className="text-gray-400"
                  />
                </>
              )}
            </svg>
          </div>

          {/* Legend */}
          {showLegend && type === "pie" && (
            <div className="mt-4 flex flex-wrap gap-4">
              {processedData.map((item: any, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: item.color }}
                  ></div>
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {item.category}: {valueFormatter(item.value)} (
                    {item.percentage.toFixed(1)}%)
                  </span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    );
  },
);

FinancialChart.displayName = "FinancialChart";

export default FinancialChart;
