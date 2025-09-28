import { useState, useEffect, useCallback } from "react";

export interface MonitoringMetrics {
  cpuUsage: number;
  memoryUsage: number;
  networkLatency: number;
  errorRate: number;
  responseTime: number;
}

export const useMonitoring = () => {
  const [metrics, setMetrics] = useState<MonitoringMetrics>({
    cpuUsage: 0,
    memoryUsage: 0,
    networkLatency: 0,
    errorRate: 0,
    responseTime: 0,
  });

  const [isMonitoring, setIsMonitoring] = useState(false);

  const startMonitoring = useCallback(() => {
    setIsMonitoring(true);
  }, []);

  const stopMonitoring = useCallback(() => {
    setIsMonitoring(false);
  }, []);

  const updateMetrics = useCallback(
    (newMetrics: Partial<MonitoringMetrics>) => {
      setMetrics((prev) => ({ ...prev, ...newMetrics }));
    },
    [],
  );

  useEffect(() => {
    if (!isMonitoring) return;

    const interval = setInterval(() => {
      // Simulate monitoring data collection
      updateMetrics({
        cpuUsage: Math.random() * 100,
        memoryUsage: Math.random() * 100,
        networkLatency: Math.random() * 1000,
        errorRate: Math.random() * 10,
        responseTime: Math.random() * 500,
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isMonitoring, updateMetrics]);

  return {
    metrics,
    isMonitoring,
    startMonitoring,
    stopMonitoring,
    updateMetrics,
  };
};
