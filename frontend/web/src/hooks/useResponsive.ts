import { useState, useEffect, useCallback } from "react";
import { designTokens } from "../design-system/DesignTokens";

type Breakpoint = keyof typeof designTokens.breakpoints;

interface ResponsiveState {
  breakpoint: Breakpoint;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  isLargeDesktop: boolean;
  width: number;
  height: number;
}

export const useResponsive = (): ResponsiveState => {
  const [state, setState] = useState<ResponsiveState>(() => {
    if (typeof window === "undefined") {
      return {
        breakpoint: "sm",
        isMobile: true,
        isTablet: false,
        isDesktop: false,
        isLargeDesktop: false,
        width: 0,
        height: 0,
      };
    }

    const width = window.innerWidth;
    const height = window.innerHeight;
    return calculateResponsiveState(width, height);
  });

  const calculateResponsiveState = useCallback(
    (width: number, height: number): ResponsiveState => {
      const breakpoints = designTokens.breakpoints;
      let breakpoint: Breakpoint = "sm";

      if (width >= parseInt(breakpoints["2xl"] as string)) {
        breakpoint = "2xl";
      } else if (width >= parseInt(breakpoints.xl)) {
        breakpoint = "xl";
      } else if (width >= parseInt(breakpoints.lg)) {
        breakpoint = "lg";
      } else if (width >= parseInt(breakpoints.md)) {
        breakpoint = "md";
      }

      return {
        breakpoint,
        isMobile: width < parseInt(breakpoints.md),
        isTablet:
          width >= parseInt(breakpoints.md) && width < parseInt(breakpoints.lg),
        isDesktop:
          width >= parseInt(breakpoints.lg) && width < parseInt(breakpoints.xl),
        isLargeDesktop: width >= parseInt(breakpoints.xl),
        width,
        height,
      };
    },
    [],
  );

  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;
      setState(calculateResponsiveState(width, height));
    };

    window.addEventListener("resize", handleResize);

    if (typeof ResizeObserver !== "undefined") {
      const resizeObserver = new ResizeObserver(handleResize);
      resizeObserver.observe(document.body);
      return () => {
        window.removeEventListener("resize", handleResize);
        resizeObserver.disconnect();
      };
    }

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, [calculateResponsiveState]);

  return state;
};

export const useResponsiveValue = <T>(
  values: Partial<Record<Breakpoint, T>>,
  defaultValue: T,
): T => {
  const { breakpoint } = useResponsive();
  const breakpoints: Breakpoint[] = ["sm", "md", "lg", "xl", "2xl"];
  const currentIndex = breakpoints.indexOf(breakpoint);

  for (let i = currentIndex; i >= 0; i--) {
    const bp = breakpoints[i];
    if (values[bp] !== undefined) {
      return values[bp] as T;
    }
  }

  return defaultValue;
};

export const useResponsiveStyles = (
  styles: Partial<Record<Breakpoint, any>>,
) => {
  const { breakpoint } = useResponsive();
  const breakpoints: Breakpoint[] = ["sm", "md", "lg", "xl", "2xl"];
  const currentIndex = breakpoints.indexOf(breakpoint);

  for (let i = currentIndex; i >= 0; i--) {
    const bp = breakpoints[i];
    if (styles[bp]) {
      return styles[bp] as any;
    }
  }

  return {};
};

export const useResponsiveClasses = (
  classes: Partial<Record<Breakpoint, string>>,
) => {
  const { breakpoint } = useResponsive();
  const breakpoints: Breakpoint[] = ["sm", "md", "lg", "xl", "2xl"];
  const currentIndex = breakpoints.indexOf(breakpoint);

  for (let i = currentIndex; i >= 0; i--) {
    const bp = breakpoints[i];
    if (classes[bp]) {
      return classes[bp] as string;
    }
  }

  return "";
};

export const useResponsiveVisibility = (
  visibility: Partial<Record<Breakpoint, boolean>>,
) => {
  const { breakpoint } = useResponsive();
  const breakpoints: Breakpoint[] = ["sm", "md", "lg", "xl", "2xl"];
  const currentIndex = breakpoints.indexOf(breakpoint);

  for (let i = currentIndex; i >= 0; i--) {
    const bp = breakpoints[i];
    if (visibility[bp] !== undefined) {
      return visibility[bp] as boolean;
    }
  }

  return true;
};

export const useResponsiveGrid = (
  columns: Partial<Record<Breakpoint, number>>,
) => {
  const { breakpoint } = useResponsive();
  const breakpoints: Breakpoint[] = ["sm", "md", "lg", "xl", "2xl"];
  const currentIndex = breakpoints.indexOf(breakpoint);

  for (let i = currentIndex; i >= 0; i--) {
    const bp = breakpoints[i];
    if (columns[bp] !== undefined) {
      return columns[bp] as number;
    }
  }

  return 1;
};

export const useResponsiveSpacing = (
  spacing: Partial<Record<Breakpoint, string>>,
) => {
  const { breakpoint } = useResponsive();
  const breakpoints: Breakpoint[] = ["sm", "md", "lg", "xl", "2xl"];
  const currentIndex = breakpoints.indexOf(breakpoint);

  for (let i = currentIndex; i >= 0; i--) {
    const bp = breakpoints[i];
    if (spacing[bp] !== undefined) {
      return spacing[bp] as string;
    }
  }

  return "0";
};

export const useResponsiveFontSize = (
  sizes: Partial<Record<Breakpoint, string>>,
) => {
  const { breakpoint } = useResponsive();
  const breakpoints: Breakpoint[] = ["sm", "md", "lg", "xl", "2xl"];
  const currentIndex = breakpoints.indexOf(breakpoint);

  for (let i = currentIndex; i >= 0; i--) {
    const bp = breakpoints[i];
    if (sizes[bp] !== undefined) {
      return sizes[bp] as string;
    }
  }

  return "1rem";
};

export default useResponsive;
