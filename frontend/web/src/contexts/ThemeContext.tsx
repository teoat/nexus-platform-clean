import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { ThemeProvider, CssBaseline } from "@mui/material";
import { createAppTheme, themeNames } from "../design-system/theme/themes";

type ThemeName = keyof typeof themeNames;

interface ThemeContextType {
  currentTheme: ThemeName;
  setTheme: (theme: ThemeName) => void;
  toggleDarkMode: () => void;
  isDarkMode: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
}

export const AppThemeProvider: React.FC<ThemeProviderProps> = ({
  children,
}) => {
  const [currentTheme, setCurrentTheme] = useState<ThemeName>(() => {
    // Get theme from localStorage or default to MODERN_MINIMAL
    const savedTheme = localStorage.getItem("app-theme") as ThemeName;
    return savedTheme && Object.keys(themeNames).includes(savedTheme)
      ? savedTheme
      : "MODERN_MINIMAL";
  });

  const [isDarkMode, setIsDarkMode] = useState(() => {
    // Check if current theme is dark mode
    return currentTheme === "DARK";
  });

  // Update dark mode state when theme changes
  useEffect(() => {
    setIsDarkMode(currentTheme === "DARK");
  }, [currentTheme]);

  const setTheme = (theme: ThemeName) => {
    setCurrentTheme(theme);
    localStorage.setItem("app-theme", theme);
  };

  const toggleDarkMode = () => {
    if (isDarkMode) {
      setTheme("MODERN_MINIMAL");
    } else {
      setTheme("DARK");
    }
  };

  const theme = createAppTheme(themeNames[currentTheme]);

  const value: ThemeContextType = {
    currentTheme,
    setTheme,
    toggleDarkMode,
    isDarkMode,
  };

  return (
    <ThemeContext.Provider value={value}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error("useTheme must be used within an AppThemeProvider");
  }
  return context;
};

export default ThemeContext;
