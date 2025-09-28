/**
 * NEXUS Platform - Performance Service
 * Real-time performance monitoring and optimization
 */

import React, { useState, useEffect, useCallback } from "react";

export interface PerformanceMetric {
  id: string;
  name: string;
  value: number;
  unit: string;
  timestamp: number;
  category: "timing" | "memory" | "network" | "rendering" | "user";
  metadata?: any;
}

export interface PerformanceReport {
  timestamp: number;
  metrics: PerformanceMetric[];
  summary: {
    totalMetrics: number;
    warnings: number;
    critical: number;
    averageScore: number;
  };
  recommendations: string[];
}

class PerformanceService {
  private metrics: PerformanceMetric[] = [];
  private listeners = new Set<(metrics: PerformanceMetric[]) => void>();

  public recordMetric(
    metric: Omit<PerformanceMetric, "id" | "timestamp">,
  ): string {
    const performanceMetric: PerformanceMetric = {
      ...metric,
      id: this.generateMetricId(),
      timestamp: Date.now(),
    };
    this.metrics.push(performanceMetric);
    if (this.metrics.length > 1000) {
      this.metrics = this.metrics.slice(-1000);
    }
    this.notifyListeners();
    return performanceMetric.id;
  }

  public recordTiming(
    name: string,
    startTime: number,
    endTime?: number,
  ): string {
    const duration = endTime
      ? endTime - startTime
      : performance.now() - startTime;
    return this.recordMetric({
      name,
      value: duration,
      unit: "ms",
      category: "timing",
    });
  }

  public getMetrics(): PerformanceMetric[] {
    return [...this.metrics].sort((a, b) => b.timestamp - a.timestamp);
  }

  public getPerformanceScore(): number {
    const recentMetrics = this.getMetrics().slice(0, 100);
    if (recentMetrics.length === 0) return 100;

    let totalScore = 0;
    let validMetrics = 0;

    recentMetrics.forEach((metric) => {
      let score = 100;
      if (metric.category === "timing" && metric.value > 1000) {
        score = Math.max(0, 100 - metric.value / 100);
      }
      totalScore += score;
      validMetrics++;
    });

    return validMetrics > 0 ? totalScore / validMetrics : 100;
  }

  public subscribe(
    listener: (metrics: PerformanceMetric[]) => void,
  ): () => void {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  private generateMetricId(): string {
    return `perf_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private notifyListeners(): void {
    this.listeners.forEach((listener) => {
      try {
        listener([...this.metrics]);
      } catch (error) {
        console.error("Error in performance listener:", error);
      }
    });
  }
}

export const performanceService = new PerformanceService();

export const usePerformanceMonitoring = () => {
  const [metrics, setMetrics] = useState<PerformanceMetric[]>([]);
  const [score, setScore] = useState(100);

  useEffect(() => {
    const unsubscribe = performanceService.subscribe((newMetrics) => {
      setMetrics(newMetrics);
      setScore(performanceService.getPerformanceScore());
    });

    setMetrics(performanceService.getMetrics());
    setScore(performanceService.getPerformanceScore());

    return unsubscribe;
  }, []);

  const recordMetric = useCallback(
    (metric: Omit<PerformanceMetric, "id" | "timestamp">) => {
      return performanceService.recordMetric(metric);
    },
    [],
  );

  const recordTiming = useCallback(
    (name: string, startTime: number, endTime?: number) => {
      return performanceService.recordTiming(name, startTime, endTime);
    },
    [],
  );

  return {
    metrics,
    score,
    recordMetric,
    recordTiming,
  };
};

export default performanceService;
