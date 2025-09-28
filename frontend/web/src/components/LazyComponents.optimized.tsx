import React, { Suspense, lazy, ComponentType } from "react";
import LoadingSpinner from "./ui/LoadingSpinner";

// Loading fallback component
const LoadingFallback = ({
  size = "medium",
}: {
  size?: "small" | "medium" | "large";
}) => (
  <div
    style={{
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      minHeight:
        size === "large" ? "400px" : size === "medium" ? "200px" : "100px",
    }}
  >
    <LoadingSpinner size={size} />
  </div>
);

// Lazy load heavy components (600+ lines)
export const LazyNexusPhaseDashboard = lazy(
  () => import("./agent/NexusPhaseDashboard"),
);
export const LazyPerformanceOptimizer = lazy(
  () => import("./performance/PerformanceOptimizer"),
);
export const LazyAnalyticsDashboard = lazy(
  () => import("./analytics/AnalyticsDashboard"),
);
export const LazyUserProfile = lazy(() => import("./financial/UserProfile"));
export const LazyUnifiedFinanceDashboard = lazy(
  () => import("./dashboard/UnifiedFinanceDashboard"),
);
export const LazyCollaborativeWorkspace = lazy(
  () => import("./collaboration/CollaborativeWorkspace"),
);
export const LazyAccountCard = lazy(() => import("./financial/AccountCard"));
export const LazyUserExperienceDashboard = lazy(
  () => import("./dashboard/UserExperienceDashboard"),
);
export const LazyAIIntelligenceDashboard = lazy(
  () => import("./dashboard/AIIntelligenceDashboard"),
);
export const LazyRealTimeDashboard = lazy(
  () => import("./dashboard/RealTimeDashboard"),
);
export const LazyAccountManagement = lazy(
  () => import("./financial/AccountManagement"),
);
export const LazyMainControlDashboard = lazy(
  () => import("./dashboard/MainControlDashboard"),
);

// Lazy load medium components (400+ lines)
export const LazyDataTable = lazy(() => import("./ui/DataTable"));
export const LazyModal = lazy(() => import("./ui/Modal"));
export const LazyCharts = lazy(() => import("./charts/ChartContainer"));
export const LazyUserManagement = lazy(() => import("./admin/UserManagement"));
export const LazyFinancialChart = lazy(
  () => import("./financial/FinancialChart"),
);
export const LazyTransactionForm = lazy(
  () => import("./financial/TransactionForm"),
);
export const LazyBulkOperations = lazy(
  () => import("./operations/BulkOperations"),
);
export const LazyPerformanceMetrics = lazy(
  () => import("./PerformanceMetrics"),
);
export const LazySecurityDashboard = lazy(() => import("./SecurityDashboard"));
export const LazySecurityManager = lazy(() => import("./SecurityManager"));
export const LazySystemHealth = lazy(() => import("./SystemHealth"));

// Lazy load pages
export const LazyDashboard = lazy(() => import("../pages/Dashboard"));
export const LazyTransactions = lazy(() => import("../pages/Transactions"));
export const LazyReports = lazy(() => import("../pages/Reports"));
export const LazySettings = lazy(() => import("../pages/Settings"));
export const LazyProfile = lazy(() => import("../pages/Profile"));
export const LazyAdmin = lazy(() => import("../pages/Admin"));
export const LazyAccounts = lazy(() => import("../pages/Accounts"));
export const LazyAnalytics = lazy(() => import("../pages/Analytics"));

// Lazy load with fallback HOC
export const withLazyLoading = <P extends object>(
  Component: ComponentType<P>,
  fallback?: React.ReactNode,
) => {
  const LazyComponent = lazy(() => Promise.resolve({ default: Component }));

  const LazyWrapper = (props: P) => (
    <Suspense fallback={fallback || <LoadingFallback />}>
      <LazyComponent {...(props as any)} />
    </Suspense>
  );
  LazyWrapper.displayName = `LazyOptimized(${Component.displayName || Component.name || "Component"})`;
  return LazyWrapper;
};

// Preload function for critical components
export const preloadComponents = () => {
  // Preload critical components on user interaction
  const preloadDataTable = () => import("./ui/DataTable");
  const preloadModal = () => import("./ui/Modal");
  const preloadCharts = () => import("./charts/ChartContainer");
  const preloadUserManagement = () => import("./admin/UserManagement");

  return {
    preloadDataTable,
    preloadModal,
    preloadCharts,
    preloadUserManagement,
  };
};

// Route-based code splitting
export const routeComponents = {
  dashboard: () => import("../pages/Dashboard"),
  transactions: () => import("../pages/Transactions"),
  reports: () => import("../pages/Reports"),
  settings: () => import("../pages/Settings"),
  profile: () => import("../pages/Profile"),
  admin: () => import("../pages/Admin"),
  accounts: () => import("../pages/Accounts"),
  analytics: () => import("../pages/Analytics"),
};

// Component-based code splitting
export const componentChunks = {
  // Heavy components (600+ lines)
  nexusPhaseDashboard: () => import("./agent/NexusPhaseDashboard"),
  performanceOptimizer: () => import("./performance/PerformanceOptimizer"),
  analyticsDashboard: () => import("./analytics/AnalyticsDashboard"),
  userProfile: () => import("./financial/UserProfile"),
  unifiedFinanceDashboard: () => import("./dashboard/UnifiedFinanceDashboard"),
  collaborativeWorkspace: () =>
    import("./collaboration/CollaborativeWorkspace"),
  accountCard: () => import("./financial/AccountCard"),
  userExperienceDashboard: () => import("./dashboard/UserExperienceDashboard"),
  aiIntelligenceDashboard: () => import("./dashboard/AIIntelligenceDashboard"),
  realTimeDashboard: () => import("./dashboard/RealTimeDashboard"),

  // Medium components (400+ lines)
  dataTable: () => import("./ui/DataTable"),
  modal: () => import("./ui/Modal"),
  charts: () => import("./charts/ChartContainer"),
  userManagement: () => import("./admin/UserManagement"),
  financialChart: () => import("./financial/FinancialChart"),
  transactionForm: () => import("./financial/TransactionForm"),
  bulkOperations: () => import("./operations/BulkOperations"),
  performanceMetrics: () => import("./PerformanceMetrics"),
  securityDashboard: () => import("./SecurityDashboard"),
  securityManager: () => import("./SecurityManager"),
  systemHealth: () => import("./SystemHealth"),
};

// Lazy wrapper components with proper error boundaries
const LazyWrapper: React.FC<{
  children: React.ReactNode;
  fallback?: React.ReactNode;
  errorFallback?: React.ReactNode;
}> = ({ children, fallback, errorFallback }): React.ReactElement => {
  const [hasError, setHasError] = React.useState(false);

  React.useEffect(() => {
    const handleError = () => setHasError(true);
    window.addEventListener("error", handleError);
    return () => window.removeEventListener("error", handleError);
  }, []);

  if (hasError) {
    return errorFallback ? (
      <>{errorFallback}</>
    ) : (
      <div>Error loading component</div>
    );
  }

  return (
    <Suspense fallback={fallback || <LoadingFallback />}>{children}</Suspense>
  );
};

// Performance monitoring for lazy loading
export const useLazyLoadingPerformance = () => {
  const [loadingTimes, setLoadingTimes] = React.useState<
    Record<string, number>
  >({});

  const trackLoadingTime = (componentName: string, startTime: number) => {
    const endTime = performance.now();
    const loadingTime = endTime - startTime;

    setLoadingTimes((prev) => ({
      ...prev,
      [componentName]: loadingTime,
    }));

    // Log slow loading components
    if (loadingTime > 1000) {
      console.warn(
        `Slow loading component: ${componentName} took ${loadingTime}ms`,
      );
    }
  };

  return { loadingTimes, trackLoadingTime };
};

// Smart preloading based on user behavior
export const useSmartPreloading = () => {
  const [preloadedComponents, setPreloadedComponents] = React.useState<
    Set<string>
  >(new Set());

  const preloadComponent = async (componentName: string) => {
    if (preloadedComponents.has(componentName)) return;

    try {
      const startTime = performance.now();
      await componentChunks[componentName as keyof typeof componentChunks]?.();
      const endTime = performance.now();

      console.log(`Preloaded ${componentName} in ${endTime - startTime}ms`);
      setPreloadedComponents((prev) => new Set([...prev, componentName]));
    } catch (error) {
      console.error(`Failed to preload ${componentName}:`, error);
    }
  };

  const preloadOnHover = (componentName: string) => {
    return {
      onMouseEnter: () => preloadComponent(componentName),
    };
  };

  return { preloadComponent, preloadOnHover, preloadedComponents };
};

LazyWrapper.displayName = "LazyWrapper";

export { LazyWrapper };

export default {
  LazyNexusPhaseDashboard,
  LazyPerformanceOptimizer,
  LazyAnalyticsDashboard,
  LazyUserProfile,
  LazyUnifiedFinanceDashboard,
  LazyCollaborativeWorkspace,
  LazyAccountCard,
  LazyUserExperienceDashboard,
  LazyAIIntelligenceDashboard,
  LazyRealTimeDashboard,
  LazyDataTable,
  LazyModal,
  LazyCharts,
  LazyUserManagement,
  LazyDashboard,
  LazyTransactions,
  LazyReports,
  LazySettings,
  LazyProfile,
  LazyAdmin,
  LazyAccounts,
  LazyAnalytics,
  withLazyLoading,
  preloadComponents,
  routeComponents,
  componentChunks,
  LazyWrapper,
  useLazyLoadingPerformance,
  useSmartPreloading,
};
