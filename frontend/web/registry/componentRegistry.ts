import PerformanceMetrics from "../src/components/PerformanceMetrics";
import SystemHealth from "../src/components/SystemHealth";
import FrenlyInsights from "../src/components/FrenlyInsights";
import InsightCard from "../src/components/InsightCard";
import FeatureManager from "../src/components/FeatureManager";
import FeatureConfig from "../src/components/FeatureConfig";
import PerformanceOptimizer from "../src/components/PerformanceOptimizer";
import OptimizationSettings from "../src/components/OptimizationSettings";
import SecurityManager from "../src/components/SecurityManager";
import SecurityDashboard from "../src/components/SecurityDashboard";
export const FrontendComponentRegistry = {
  PerformanceMetrics,
  SystemHealth,
  FrenlyInsights,
  InsightCard,
  FeatureManager,
  FeatureConfig,
  PerformanceOptimizer,
  OptimizationSettings,
  SecurityManager,
  SecurityDashboard,
};
export const getComponent = (name: string) => {
  return FrontendComponentRegistry[
    name as keyof typeof FrontendComponentRegistry
  ];
};
export const getAllComponents = () => {
  return Object.keys(FrontendComponentRegistry);
};
