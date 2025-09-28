/**
 * NEXUS Platform - Components Barrel Export
 * Centralized exports for optimized tree shaking
 */

// Design System Components
export { Button } from "./design-system/Button";
export { Card } from "./design-system/Card";

// UI Components
export { default as Alert } from "./ui/Alert";
export { default as Badge } from "./ui/Badge";
export { default as UIButton } from "./ui/Button";
export { default as UICard } from "./ui/Card";
export { default as Checkbox } from "./ui/Checkbox";
export { default as DataTable } from "./ui/DataTable";
export { default as Input } from "./ui/Input";
export { default as LoadingSpinner } from "./ui/LoadingSpinner";
export { default as Modal } from "./ui/Modal";
export { default as Progress } from "./ui/Progress";
export { default as RadioGroup } from "./ui/Radio";
export { default as Select } from "./ui/Select";
export { default as Switch } from "./ui/Switch";
export { default as Textarea } from "./ui/Textarea";
export { FormField } from "./ui/FormField";

// Common Components
export { Chart } from "./common/Chart";
export { StatusIndicator } from "./common/StatusIndicator";

// Dashboard Components
export { default as FinancialDashboard } from "./dashboard/FinancialDashboard";
export { RealTimeDashboard } from "./dashboard/RealTimeDashboard";
export { default as UnifiedFinanceDashboard } from "./dashboard/UnifiedFinanceDashboard";
export { default as AnalyticsDashboard } from "./analytics/AnalyticsDashboard";
export { default as AIIntelligenceDashboard } from "./dashboard/AIIntelligenceDashboard";
export { default as UserExperienceDashboard } from "./dashboard/UserExperienceDashboard";

// Financial Components
export { default as AccountManagement } from "./financial/AccountManagement";
export { default as AccountCard } from "./financial/AccountCard";
export { default as TransactionForm } from "./financial/TransactionForm";
export { default as UserProfile } from "./financial/UserProfile";

// Auth Components
export { default as LoginForm } from "./auth/LoginForm";
export { default as RegisterForm } from "./auth/RegisterForm";
export { default as EnhancedLoginForm } from "./auth/EnhancedLoginForm";
export { default as POVSelection } from "./auth/POVSelection";

// Frenly AI Components
export { default as FrenlyAIInterface } from "./frenly/FrenlyAIInterface";
export { default as FrenlyInsights } from "./ai/FrenlyInsights";

// Performance Components
export { default as PerformanceOptimizer } from "./performance/PerformanceOptimizer";

// Operations Components
export { default as BulkOperations } from "./operations/BulkOperations";

// Admin Components
export { default as UserManagement } from "./admin/UserManagement";

// Feature Components
export { default as FeatureConfig } from "./FeatureConfig";
export { default as FeatureManager } from "./FeatureManager";
export { default as OptimizationSettings } from "./OptimizationSettings";
export { default as PerformanceMetrics } from "./PerformanceMetrics";
export { default as SecurityDashboard } from "./SecurityDashboard";
export { default as SecurityManager } from "./SecurityManager";
export { default as SystemHealth } from "./SystemHealth";

// Lazy Components
export { LazyComponents } from "../utils/lazyLoading";
