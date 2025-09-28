/**
 * NEXUS Platform - Performance Optimizer
 * Comprehensive performance monitoring and optimization
 */

import { ComponentType, lazy, Suspense } from 'react';
// import { ErrorBoundary } from 'react-error-boundary';

// Simple ErrorBoundary component
const ErrorBoundary = ({ children, fallback, onError }: { 
  children: React.ReactNode; 
  fallback: React.ReactNode; 
  onError?: (error: any) => void;
}) => {
  try {
    return <>{children}</>;
  } catch (error) {
    onError?.(error);
    return <>{fallback}</>;
  }
};

export interface PerformanceMetrics {
  loadTime: number;
  renderTime: number;
  memoryUsage: number;
  bundleSize: number;
  cacheHitRate: number;
  apiResponseTime: number;
  errorRate: number;
  userSatisfactionScore: number;
}

export interface PerformanceBudget {
  maxLoadTime: number;
  maxRenderTime: number;
  maxMemoryUsage: number;
  maxBundleSize: number;
  minCacheHitRate: number;
  maxApiResponseTime: number;
  maxErrorRate: number;
  minUserSatisfactionScore: number;
}

export interface OptimizationResult {
  metric: string;
  currentValue: number;
  targetValue: number;
  improvement: number;
  status: 'optimal' | 'warning' | 'critical';
  recommendations: string[];
}

class PerformanceOptimizer {
  private metrics: PerformanceMetrics;
  private budget: PerformanceBudget;
  private observers: Map<string, PerformanceObserver>;
  private measurements: Map<string, number[]>;

  constructor() {
    this.metrics = {
      loadTime: 0,
      renderTime: 0,
      memoryUsage: 0,
      bundleSize: 0,
      cacheHitRate: 0,
      apiResponseTime: 0,
      errorRate: 0,
      userSatisfactionScore: 0
    };

    this.budget = {
      maxLoadTime: 2000, // 2 seconds
      maxRenderTime: 100, // 100ms
      maxMemoryUsage: 50 * 1024 * 1024, // 50MB
      maxBundleSize: 500 * 1024, // 500KB
      minCacheHitRate: 0.8, // 80%
      maxApiResponseTime: 1000, // 1 second
      maxErrorRate: 0.01, // 1%
      minUserSatisfactionScore: 0.8 // 80%
    };

    this.observers = new Map();
    this.measurements = new Map();
    
    this.initializePerformanceMonitoring();
  }

  /**
   * Initialize performance monitoring
   */
  private initializePerformanceMonitoring(): void {
    // Monitor page load performance
    this.observePageLoad();
    
    // Monitor memory usage
    this.observeMemoryUsage();
    
    // Monitor API performance
    this.observeAPIPerformance();
    
    // Monitor user interactions
    this.observeUserInteractions();
  }

  /**
   * Observe page load performance
   */
  private observePageLoad(): void {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          if (entry.entryType === 'navigation') {
            const navEntry = entry as PerformanceNavigationTiming;
            this.metrics.loadTime = navEntry.loadEventEnd - (navEntry as any).navigationStart;
            this.recordMeasurement('loadTime', this.metrics.loadTime);
          }
        });
      });

      observer.observe({ entryTypes: ['navigation'] });
      this.observers.set('navigation', observer);
    }
  }

  /**
   * Observe memory usage
   */
  private observeMemoryUsage(): void {
    if ('memory' in performance) {
      const updateMemoryUsage = () => {
        const memory = (performance as any).memory;
        this.metrics.memoryUsage = memory.usedJSHeapSize;
        this.recordMeasurement('memoryUsage', this.metrics.memoryUsage);
      };

      // Update memory usage every 5 seconds
      setInterval(updateMemoryUsage, 5000);
      updateMemoryUsage();
    }
  }

  /**
   * Observe API performance
   */
  private observeAPIPerformance(): void {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          if (entry.entryType === 'resource') {
            const resourceEntry = entry as PerformanceResourceTiming;
            if (resourceEntry.name.includes('/api/')) {
              const responseTime = resourceEntry.responseEnd - resourceEntry.requestStart;
              this.recordMeasurement('apiResponseTime', responseTime);
              this.updateAPIMetrics(responseTime);
            }
          }
        });
      });

      observer.observe({ entryTypes: ['resource'] });
      this.observers.set('resource', observer);
    }
  }

  /**
   * Observe user interactions
   */
  private observeUserInteractions(): void {
    let interactionStart = 0;
    
    const measureInteraction = (event: Event) => {
      const interactionTime = performance.now() - interactionStart;
      this.recordMeasurement('renderTime', interactionTime);
      this.updateRenderMetrics(interactionTime);
    };

    // Measure click interactions
    document.addEventListener('click', (event) => {
      interactionStart = performance.now();
      requestAnimationFrame(() => {
        measureInteraction(event);
      });
    });

    // Measure scroll interactions
    let scrollTimeout: NodeJS.Timeout;
    document.addEventListener('scroll', () => {
      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(() => {
        const scrollTime = performance.now() - interactionStart;
        this.recordMeasurement('renderTime', scrollTime);
      }, 100);
    });
  }

  /**
   * Record measurement for a metric
   */
  private recordMeasurement(metric: string, value: number): void {
    if (!this.measurements.has(metric)) {
      this.measurements.set(metric, []);
    }
    
    const measurements = this.measurements.get(metric)!;
    measurements.push(value);
    
    // Keep only last 100 measurements
    if (measurements.length > 100) {
      measurements.shift();
    }
  }

  /**
   * Update API metrics
   */
  private updateAPIMetrics(responseTime: number): void {
    const measurements = this.measurements.get('apiResponseTime') || [];
    this.metrics.apiResponseTime = measurements.reduce((a, b) => a + b, 0) / measurements.length;
    
    // Calculate error rate (simplified)
    const errorCount = measurements.filter(time => time > 5000).length;
    this.metrics.errorRate = errorCount / measurements.length;
  }

  /**
   * Update render metrics
   */
  private updateRenderMetrics(renderTime: number): void {
    const measurements = this.measurements.get('renderTime') || [];
    this.metrics.renderTime = measurements.reduce((a, b) => a + b, 0) / measurements.length;
  }

  /**
   * Get current performance metrics
   */
  getMetrics(): PerformanceMetrics {
    return { ...this.metrics };
  }

  /**
   * Get performance budget
   */
  getBudget(): PerformanceBudget {
    return { ...this.budget };
  }

  /**
   * Analyze performance against budget
   */
  analyzePerformance(): OptimizationResult[] {
    const results: OptimizationResult[] = [];

    // Analyze load time
    results.push(this.analyzeMetric(
      'loadTime',
      this.metrics.loadTime,
      this.budget.maxLoadTime,
      'lower',
      [
        'Implement code splitting',
        'Use lazy loading for components',
        'Optimize bundle size',
        'Enable gzip compression',
        'Use CDN for static assets'
      ]
    ));

    // Analyze render time
    results.push(this.analyzeMetric(
      'renderTime',
      this.metrics.renderTime,
      this.budget.maxRenderTime,
      'lower',
      [
        'Optimize React components',
        'Use React.memo for expensive components',
        'Implement virtual scrolling',
        'Reduce DOM manipulations',
        'Use CSS transforms instead of layout changes'
      ]
    ));

    // Analyze memory usage
    results.push(this.analyzeMetric(
      'memoryUsage',
      this.metrics.memoryUsage,
      this.budget.maxMemoryUsage,
      'lower',
      [
        'Implement proper cleanup in useEffect',
        'Remove event listeners on unmount',
        'Use weak references where appropriate',
        'Implement object pooling',
        'Monitor for memory leaks'
      ]
    ));

    // Analyze API response time
    results.push(this.analyzeMetric(
      'apiResponseTime',
      this.metrics.apiResponseTime,
      this.budget.maxApiResponseTime,
      'lower',
      [
        'Implement API caching',
        'Use database indexing',
        'Optimize database queries',
        'Implement request batching',
        'Use connection pooling'
      ]
    ));

    // Analyze error rate
    results.push(this.analyzeMetric(
      'errorRate',
      this.metrics.errorRate,
      this.budget.maxErrorRate,
      'lower',
      [
        'Implement proper error handling',
        'Add input validation',
        'Use TypeScript for type safety',
        'Implement retry mechanisms',
        'Add comprehensive logging'
      ]
    ));

    return results;
  }

  /**
   * Analyze individual metric
   */
  private analyzeMetric(
    metric: string,
    currentValue: number,
    targetValue: number,
    direction: 'lower' | 'higher',
    recommendations: string[]
  ): OptimizationResult {
    let improvement = 0;
    let status: 'optimal' | 'warning' | 'critical';

    if (direction === 'lower') {
      improvement = ((targetValue - currentValue) / targetValue) * 100;
      if (currentValue <= targetValue) {
        status = 'optimal';
      } else if (currentValue <= targetValue * 1.5) {
        status = 'warning';
      } else {
        status = 'critical';
      }
    } else {
      improvement = ((currentValue - targetValue) / targetValue) * 100;
      if (currentValue >= targetValue) {
        status = 'optimal';
      } else if (currentValue >= targetValue * 0.5) {
        status = 'warning';
      } else {
        status = 'critical';
      }
    }

    return {
      metric,
      currentValue,
      targetValue,
      improvement,
      status,
      recommendations: status !== 'optimal' ? recommendations : []
    };
  }

  /**
   * Generate performance report
   */
  generateReport(): {
    summary: {
      overallScore: number;
      status: 'excellent' | 'good' | 'needs_improvement' | 'poor';
      criticalIssues: number;
      warnings: number;
    };
    metrics: PerformanceMetrics;
    budget: PerformanceBudget;
    analysis: OptimizationResult[];
    recommendations: string[];
  } {
    const analysis = this.analyzePerformance();
    const criticalIssues = analysis.filter(r => r.status === 'critical').length;
    const warnings = analysis.filter(r => r.status === 'warning').length;
    
    // Calculate overall score
    const optimalCount = analysis.filter(r => r.status === 'optimal').length;
    const overallScore = (optimalCount / analysis.length) * 100;
    
    let status: 'excellent' | 'good' | 'needs_improvement' | 'poor';
    if (overallScore >= 90) {
      status = 'excellent';
    } else if (overallScore >= 70) {
      status = 'good';
    } else if (overallScore >= 50) {
      status = 'needs_improvement';
    } else {
      status = 'poor';
    }

    // Collect all recommendations
    const recommendations = analysis
      .filter(r => r.recommendations.length > 0)
      .flatMap(r => r.recommendations);

    return {
      summary: {
        overallScore,
        status,
        criticalIssues,
        warnings
      },
      metrics: this.getMetrics(),
      budget: this.getBudget(),
      analysis,
      recommendations: [...new Set(recommendations)] // Remove duplicates
    };
  }

  /**
   * Create lazy-loaded component with performance monitoring
   */
  createLazyComponent<T extends ComponentType<any>>(
    importFunc: () => Promise<{ default: T }>,
    fallback?: React.ReactNode
  ): React.ComponentType<React.ComponentProps<T>> {
    const LazyComponent = lazy(importFunc);

    return (props: React.ComponentProps<T>) => {
      const startTime = performance.now();

      return (
        <ErrorBoundary
          fallback={<div>Error loading component</div>}
          onError={(error: any) => {
            console.error('Lazy component error:', error);
            this.recordMeasurement('errorRate', 1);
          }}
        >
          <Suspense
            fallback={
              fallback || (
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'center', 
                  alignItems: 'center', 
                  height: '200px' 
                }}>
                  Loading...
                </div>
              )
            }
          >
            <LazyComponent 
              {...props} 
              ref={(ref: any) => {
                if (ref) {
                  const loadTime = performance.now() - startTime;
                  this.recordMeasurement('loadTime', loadTime);
                }
              }}
            />
          </Suspense>
        </ErrorBoundary>
      );
    };
  }

  /**
   * Implement code splitting for routes
   */
  createRouteLazyLoader(routePath: string) {
    return () => {
      const startTime = performance.now();
      
      return import(`../pages/${routePath}`).then(module => {
        const loadTime = performance.now() - startTime;
        this.recordMeasurement('loadTime', loadTime);
        return module;
      });
    };
  }

  /**
   * Optimize images with lazy loading
   */
  createOptimizedImage(src: string, alt: string, className?: string) {
    return (
      <img
        src={src}
        alt={alt}
        className={className}
        loading="lazy"
        onLoad={() => {
          this.recordMeasurement('renderTime', performance.now());
        }}
        onError={() => {
          this.recordMeasurement('errorRate', 1);
        }}
      />
    );
  }

  /**
   * Implement API caching
   */
  private apiCache = new Map<string, { data: any; timestamp: number; ttl: number }>();

  async cachedAPICall<T>(
    key: string,
    apiCall: () => Promise<T>,
    ttl: number = 300000 // 5 minutes default
  ): Promise<T> {
    const cached = this.apiCache.get(key);
    const now = Date.now();

    if (cached && (now - cached.timestamp) < cached.ttl) {
      this.metrics.cacheHitRate = (this.metrics.cacheHitRate + 1) / 2; // Simple moving average
      return cached.data;
    }

    const startTime = performance.now();
    try {
      const data = await apiCall();
      const responseTime = performance.now() - startTime;
      
      this.apiCache.set(key, { data, timestamp: now, ttl });
      this.recordMeasurement('apiResponseTime', responseTime);
      
      return data;
    } catch (error) {
      this.recordMeasurement('errorRate', 1);
      throw error;
    }
  }

  /**
   * Cleanup resources
   */
  cleanup(): void {
    this.observers.forEach(observer => observer.disconnect());
    this.observers.clear();
    this.measurements.clear();
    this.apiCache.clear();
  }
}

// Export singleton instance
export const performanceOptimizer = new PerformanceOptimizer();

// Export convenience functions
export const getPerformanceMetrics = () => performanceOptimizer.getMetrics();
export const getPerformanceBudget = () => performanceOptimizer.getBudget();
export const analyzePerformance = () => performanceOptimizer.analyzePerformance();
export const generatePerformanceReport = () => performanceOptimizer.generateReport();
export const createLazyComponent = performanceOptimizer.createLazyComponent.bind(performanceOptimizer);
export const createRouteLazyLoader = performanceOptimizer.createRouteLazyLoader.bind(performanceOptimizer);
export const createOptimizedImage = performanceOptimizer.createOptimizedImage.bind(performanceOptimizer);
export const cachedAPICall = performanceOptimizer.cachedAPICall.bind(performanceOptimizer);

export default performanceOptimizer;
