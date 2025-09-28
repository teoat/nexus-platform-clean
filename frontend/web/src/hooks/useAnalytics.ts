import { useCallback } from "react";

export interface AnalyticsEvent {
  name: string;
  properties?: Record<string, any>;
  timestamp?: number;
}

export const useAnalytics = () => {
  const trackEvent = useCallback((event: AnalyticsEvent) => {
    // In a real application, this would send data to an analytics service
    console.log("Analytics Event:", event);
  }, []);

  const trackPageView = useCallback(
    (page: string) => {
      trackEvent({
        name: "page_view",
        properties: { page },
      });
    },
    [trackEvent],
  );

  const trackUserAction = useCallback(
    (action: string, properties?: Record<string, any>) => {
      trackEvent({
        name: "user_action",
        properties: { action, ...properties },
      });
    },
    [trackEvent],
  );

  const trackError = useCallback(
    (error: string, properties?: Record<string, any>) => {
      trackEvent({
        name: "error",
        properties: { error, ...properties },
      });
    },
    [trackEvent],
  );

  return {
    trackEvent,
    trackPageView,
    trackUserAction,
    trackError,
  };
};
