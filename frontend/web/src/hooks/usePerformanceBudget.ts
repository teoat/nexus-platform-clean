import { useState, useEffect, useCallback } from 'react';

export interface PerformanceBudget {
  maxBundleSize: number;
  maxLoadTime: number;
  maxMemoryUsage: number;
  maxCpuUsage: number;
  maxApiResponseTime: number;
  maxCacheSize: number;
  maxAliasResolutionTime: number;
}

export interface PerformanceMetrics {
  bundleSize: number;
  loadTime: number;
  memoryUsage: number;
  cpuUsage: number;
  apiResponseTime: number;
  cacheSize: number;
  aliasResolutionTime: number;
  ssotCacheHits: number;
  ssotCacheMisses: number;
  totalApiCalls: number;
  failedApiCalls: number;
}

export const usePerformanceBudget = () => {
  const [budget, setBudget] = useState<PerformanceBudget>({
    maxBundleSize: 500 * 1024, // 500KB
    maxLoadTime: 3000, // 3 seconds
    maxMemoryUsage: 50 * 1024 * 1024, // 50MB
    maxCpuUsage: 80, // 80%
    maxApiResponseTime: 2000, // 2 seconds
    maxCacheSize: 100, // 100 cached items
    maxAliasResolutionTime: 100, // 100ms
  });

  const [currentMetrics, setCurrentMetrics] = useState<PerformanceMetrics>({
    bundleSize: 0,
    loadTime: 0,
    memoryUsage: 0,
    cpuUsage: 0,
    apiResponseTime: 0,
    cacheSize: 0,
    aliasResolutionTime: 0,
    ssotCacheHits: 0,
    ssotCacheMisses: 0,
    totalApiCalls: 0,
    failedApiCalls: 0,
  });

  const updateBudget = useCallback((newBudget: Partial<PerformanceBudget>) => {
    setBudget(prev => ({ ...prev, ...newBudget }));
  }, []);

  const checkBudget = useCallback(() => {
    const violations = [];

    if (currentMetrics.bundleSize > budget.maxBundleSize) {
      violations.push(
        `Bundle size ${currentMetrics.bundleSize} exceeds budget ${budget.maxBundleSize}`
      );
    }

    if (currentMetrics.loadTime > budget.maxLoadTime) {
      violations.push(
        `Load time ${currentMetrics.loadTime}ms exceeds budget ${budget.maxLoadTime}ms`
      );
    }

    if (currentMetrics.memoryUsage > budget.maxMemoryUsage) {
      violations.push(
        `Memory usage ${currentMetrics.memoryUsage} exceeds budget ${budget.maxMemoryUsage}`
      );
    }

    if (currentMetrics.cpuUsage > budget.maxCpuUsage) {
      violations.push(
        `CPU usage ${currentMetrics.cpuUsage}% exceeds budget ${budget.maxCpuUsage}%`
      );
    }

    if (currentMetrics.apiResponseTime > budget.maxApiResponseTime) {
      violations.push(
        `API response time ${currentMetrics.apiResponseTime}ms exceeds budget ${budget.maxApiResponseTime}ms`
      );
    }

    if (currentMetrics.cacheSize > budget.maxCacheSize) {
      violations.push(
        `Cache size ${currentMetrics.cacheSize} exceeds budget ${budget.maxCacheSize}`
      );
    }

    if (currentMetrics.aliasResolutionTime > budget.maxAliasResolutionTime) {
      violations.push(
        `Alias resolution time ${currentMetrics.aliasResolutionTime}ms exceeds budget ${budget.maxAliasResolutionTime}ms`
      );
    }

    return violations;
  }, [currentMetrics, budget]);

  const updateMetrics = useCallback((metrics: Partial<PerformanceMetrics>) => {
    setCurrentMetrics(prev => ({ ...prev, ...metrics }));
  }, []);

  // SSOT-specific performance tracking
  const trackApiCall = useCallback((responseTime: number, success: boolean) => {
    setCurrentMetrics(prev => ({
      ...prev,
      apiResponseTime: responseTime,
      totalApiCalls: prev.totalApiCalls + 1,
      failedApiCalls: success ? prev.failedApiCalls : prev.failedApiCalls + 1,
    }));
  }, []);

  const trackAliasResolution = useCallback(
    (resolutionTime: number, cacheHit: boolean) => {
      setCurrentMetrics(prev => ({
        ...prev,
        aliasResolutionTime: resolutionTime,
        ssotCacheHits: cacheHit ? prev.ssotCacheHits + 1 : prev.ssotCacheHits,
        ssotCacheMisses: cacheHit
          ? prev.ssotCacheMisses
          : prev.ssotCacheMisses + 1,
      }));
    },
    []
  );

  const trackCacheSize = useCallback((size: number) => {
    setCurrentMetrics(prev => ({
      ...prev,
      cacheSize: size,
    }));
  }, []);

  // Performance score calculation
  const getPerformanceScore = useCallback(() => {
    const violations = checkBudget();
    const totalChecks = 7; // Number of budget checks
    const violationsCount = violations.length;
    return Math.max(
      0,
      Math.round(((totalChecks - violationsCount) / totalChecks) * 100)
    );
  }, [checkBudget]);

  // Cache hit rate calculation
  const getCacheHitRate = useCallback(() => {
    const total = currentMetrics.ssotCacheHits + currentMetrics.ssotCacheMisses;
    return total > 0
      ? Math.round((currentMetrics.ssotCacheHits / total) * 100)
      : 0;
  }, [currentMetrics.ssotCacheHits, currentMetrics.ssotCacheMisses]);

  // API success rate calculation
  const getApiSuccessRate = useCallback(() => {
    return currentMetrics.totalApiCalls > 0
      ? Math.round(
          ((currentMetrics.totalApiCalls - currentMetrics.failedApiCalls) /
            currentMetrics.totalApiCalls) *
            100
        )
      : 100;
  }, [currentMetrics.totalApiCalls, currentMetrics.failedApiCalls]);

  // Auto-monitoring setup
  useEffect(() => {
    const monitorPerformance = () => {
      // Monitor memory usage
      if ('memory' in performance) {
        const memory = (performance as any).memory;
        if (memory) {
          updateMetrics({
            memoryUsage: memory.usedJSHeapSize,
          });
        }
      }

      // Monitor page load time
      if (performance.timing) {
        const loadTime =
          performance.timing.loadEventEnd - performance.timing.navigationStart;
        updateMetrics({ loadTime });
      }
    };

    // Initial measurement
    monitorPerformance();

    // Set up periodic monitoring
    const interval = setInterval(monitorPerformance, 5000);

    return () => clearInterval(interval);
  }, [updateMetrics]);

  return {
    budget,
    currentMetrics,
    updateBudget,
    updateMetrics,
    checkBudget,
    trackApiCall,
    trackAliasResolution,
    trackCacheSize,
    getPerformanceScore,
    getCacheHitRate,
    getApiSuccessRate,
  };
};
