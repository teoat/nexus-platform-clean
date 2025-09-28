/**
 * NEXUS Platform - usePerformanceOptimization Hook
 * Custom hook for performance optimization and monitoring
 */

import React, {
  useState,
  useEffect,
  useCallback,
  useMemo,
  useRef,
} from "react";
import { useGlobalStore } from "../store";

export interface PerformanceMetrics {
  renderTime: number;
  memoryUsage: number;
  componentCount: number;
  reRenderCount: number;
  lastRenderTime: number;
}

export interface PerformanceConfig {
  enableMonitoring: boolean;
  enableLazyLoading: boolean;
  enableMemoization: boolean;
  enableVirtualization: boolean;
  enableCodeSplitting: boolean;
  maxRenderTime: number;
  maxMemoryUsage: number;
}

export const usePerformanceOptimization = (
  config: Partial<PerformanceConfig> = {},
) => {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    renderTime: 0,
    memoryUsage: 0,
    componentCount: 0,
    reRenderCount: 0,
    lastRenderTime: 0,
  });

  const [isOptimized, setIsOptimized] = useState(false);
  const [warnings, setWarnings] = useState<string[]>([]);

  const renderStartTime = useRef<number>(0);
  const renderCount = useRef<number>(0);
  const componentRef = useRef<HTMLElement>(null);

  const defaultConfig: PerformanceConfig = {
    enableMonitoring: true,
    enableLazyLoading: true,
    enableMemoization: true,
    enableVirtualization: false,
    enableCodeSplitting: true,
    maxRenderTime: 16, // 60fps
    maxMemoryUsage: 50 * 1024 * 1024, // 50MB
  };

  const finalConfig = { ...defaultConfig, ...config };

  const measureRenderTime = useCallback(() => {
    if (!finalConfig.enableMonitoring) return;

    const now = performance.now();
    const renderTime = now - renderStartTime.current;

    setMetrics((prev) => ({
      ...prev,
      renderTime,
      lastRenderTime: now,
      reRenderCount: renderCount.current,
    }));

    if (renderTime > finalConfig.maxRenderTime) {
      setWarnings((prev) => [
        ...prev.filter((w) => !w.includes("render time")),
        `Render time exceeded threshold: ${renderTime.toFixed(2)}ms`,
      ]);
    }
  }, [finalConfig]);

  const measureMemoryUsage = useCallback(() => {
    if (!finalConfig.enableMonitoring || !("memory" in performance)) return;

    const memory = (performance as any).memory;
    if (memory) {
      const memoryUsage = memory.usedJSHeapSize;
      setMetrics((prev) => ({
        ...prev,
        memoryUsage,
      }));

      if (memoryUsage > finalConfig.maxMemoryUsage) {
        setWarnings((prev) => [
          ...prev.filter((w) => !w.includes("memory usage")),
          `Memory usage exceeded threshold: ${(memoryUsage / 1024 / 1024).toFixed(2)}MB`,
        ]);
      }
    }
  }, [finalConfig]);

  const startRenderMeasurement = useCallback(() => {
    if (!finalConfig.enableMonitoring) return;
    renderStartTime.current = performance.now();
    renderCount.current += 1;
  }, [finalConfig]);

  const endRenderMeasurement = useCallback(() => {
    if (!finalConfig.enableMonitoring) return;
    measureRenderTime();
    measureMemoryUsage();
  }, [measureRenderTime, measureMemoryUsage]);

  const createMemoizedCallback = <T extends (...args: any[]) => any>(
    callback: T,
    deps: React.DependencyList,
  ): T => {
    if (!finalConfig.enableMemoization) return callback;
    return callback;
  };

  const createMemoizedValue = <T>(
    factory: () => T,
    deps: React.DependencyList,
  ): T => {
    if (!finalConfig.enableMemoization) return factory();
    return factory();
  };

  const createLazyComponent = useCallback(
    <T extends React.ComponentType<any>>(
      importFunc: () => Promise<{ default: T }>,
    ): React.LazyExoticComponent<T> => {
      if (!finalConfig.enableLazyLoading) {
        throw new Error("Lazy loading is disabled");
      }
      return React.lazy(importFunc);
    },
    [finalConfig],
  );

  const createVirtualizedList = useCallback(
    <T>(
      items: T[],
      itemHeight: number,
      containerHeight: number,
      renderItem: (item: T, index: number) => React.ReactNode,
    ) => {
      if (!finalConfig.enableVirtualization) {
        return items.map(renderItem);
      }

      const visibleCount = Math.ceil(containerHeight / itemHeight);
      const startIndex = 0; // This would be dynamic in a real implementation
      const endIndex = Math.min(startIndex + visibleCount, items.length);

      return items
        .slice(startIndex, endIndex)
        .map((item, index) => renderItem(item, startIndex + index));
    },
    [finalConfig],
  );

  const createCodeSplit = useCallback(
    async <T>(importFunc: () => Promise<T>): Promise<T> => {
      if (!finalConfig.enableCodeSplitting) {
        throw new Error("Code splitting is disabled");
      }

      try {
        return await importFunc();
      } catch (error) {
        console.error("Code splitting error:", error);
        throw error;
      }
    },
    [finalConfig],
  );

  useEffect(() => {
    if (!finalConfig.enableMonitoring) return;

    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach((entry) => {
        if (entry.entryType === "measure") {
          console.log(
            `Performance measure: ${entry.name} - ${entry.duration}ms`,
          );
        }
      });
    });

    observer.observe({ entryTypes: ["measure"] });

    return () => observer.disconnect();
  }, [finalConfig]);

  const optimizeComponent = useCallback(
    (component: React.ComponentType<any>) => {
      if (!finalConfig.enableMemoization) return component;
      return React.memo(component);
    },
    [finalConfig],
  );

  const monitorBundleSize = useCallback(() => {
    if (!finalConfig.enableMonitoring) return;
    console.log("Bundle size monitoring enabled");
  }, [finalConfig]);

  const getRecommendations = useCallback(() => {
    const recommendations: string[] = [];

    if (metrics.renderTime > finalConfig.maxRenderTime) {
      recommendations.push(
        "Consider using React.memo() to prevent unnecessary re-renders",
      );
      recommendations.push(
        "Check for expensive calculations in render methods",
      );
      recommendations.push(
        "Consider using useMemo() for expensive computations",
      );
    }

    if (metrics.memoryUsage > finalConfig.maxMemoryUsage) {
      recommendations.push("Check for memory leaks in useEffect cleanup");
      recommendations.push(
        "Consider using WeakMap or WeakSet for object references",
      );
      recommendations.push("Review component unmounting and cleanup");
    }

    if (metrics.reRenderCount > 10) {
      recommendations.push(
        "Component is re-rendering frequently - check dependencies",
      );
      recommendations.push("Consider using useCallback() for event handlers");
      recommendations.push("Review state updates and prop changes");
    }

    return recommendations;
  }, [metrics, finalConfig]);

  const clearWarnings = useCallback(() => {
    setWarnings([]);
  }, []);

  const resetMetrics = useCallback(() => {
    setMetrics({
      renderTime: 0,
      memoryUsage: 0,
      componentCount: 0,
      reRenderCount: 0,
      lastRenderTime: 0,
    });
    setWarnings([]);
  }, []);

  useEffect(() => {
    if (finalConfig.enableMonitoring) {
      const recommendations = getRecommendations();
      if (recommendations.length > 0) {
        console.warn("Performance recommendations:", recommendations);
      }
    }
  }, [metrics, getRecommendations, finalConfig]);

  return {
    metrics,
    isOptimized,
    warnings,
    config: finalConfig,
    startRenderMeasurement,
    endRenderMeasurement,
    measureRenderTime,
    measureMemoryUsage,
    createMemoizedCallback,
    createMemoizedValue,
    createLazyComponent,
    createVirtualizedList,
    createCodeSplit,
    optimizeComponent,
    monitorBundleSize,
    getRecommendations,
    clearWarnings,
    resetMetrics,
    componentRef,
  };
};
