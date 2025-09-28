import React, { Suspense, lazy } from "react";
import LoadingSpinner from "./ui/LoadingSpinner";

// Lazy load heavy components
export const LazyDataTable = lazy(() => import("./ui/DataTable"));
export const LazyModal = lazy(() => import("./ui/Modal"));
export const LazyCharts = lazy(() => import("./charts/ChartContainer"));
export const LazyFinancialDashboard = lazy(
  () => import("./dashboard/FinancialDashboard"),
);
export const LazyUserManagement = lazy(() => import("./admin/UserManagement"));

// Lazy load pages
export const LazyDashboard = lazy(() => import("../pages/Dashboard"));
export const LazyTransactions = lazy(() => import("../pages/Transactions"));
export const LazyReports = lazy(() => import("../pages/Reports"));
export const LazySettings = lazy(() => import("../pages/Settings"));

// Lazy load with fallback
export const withLazyLoading = <P extends object>(
  Component: React.ComponentType<P>,
  fallback?: React.ReactNode,
) => {
  const LazyComponent = lazy(() => Promise.resolve({ default: Component }));

  const LazyWrapper = (props: P) => (
    <Suspense fallback={fallback || <LoadingSpinner size="medium" />}>
      <LazyComponent {...(props as any)} />
    </Suspense>
  );
  LazyWrapper.displayName = `Lazy(${Component.displayName || Component.name || "Component"})`;
  return LazyWrapper;
};

// Preload function for critical components
export const preloadComponents = () => {
  // Preload critical components on user interaction
  const preloadDataTable = () => import("./ui/DataTable");
  const preloadModal = () => import("./ui/Modal");

  return {
    preloadDataTable,
    preloadModal,
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
};
