import { createTheme, ThemeOptions } from "@mui/material/styles";

export const themeNames = {
  LIGHT: "light",
  DARK: "dark",
  NEXUS: "nexus",
  MODERN_MINIMAL: "modern_minimal",
} as const;

export type ThemeName = (typeof themeNames)[keyof typeof themeNames];

const lightThemeOptions: ThemeOptions = {
  palette: {
    mode: "light",
    primary: {
      main: "#1976d2",
      light: "#42a5f5",
      dark: "#1565c0",
    },
    secondary: {
      main: "#dc004e",
      light: "#ff5983",
      dark: "#9a0036",
    },
    background: {
      default: "#f5f5f5",
      paper: "#ffffff",
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 8,
  },
};

const darkThemeOptions: ThemeOptions = {
  palette: {
    mode: "dark",
    primary: {
      main: "#90caf9",
      light: "#e3f2fd",
      dark: "#42a5f5",
    },
    secondary: {
      main: "#f48fb1",
      light: "#fce4ec",
      dark: "#c2185b",
    },
    background: {
      default: "#121212",
      paper: "#1e1e1e",
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 8,
  },
};

const nexusThemeOptions: ThemeOptions = {
  palette: {
    mode: "light",
    primary: {
      main: "#6366f1",
      light: "#818cf8",
      dark: "#4f46e5",
    },
    secondary: {
      main: "#f59e0b",
      light: "#fbbf24",
      dark: "#d97706",
    },
    background: {
      default: "#f8fafc",
      paper: "#ffffff",
    },
    success: {
      main: "#10b981",
    },
    warning: {
      main: "#f59e0b",
    },
    error: {
      main: "#ef4444",
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 700,
      letterSpacing: "-0.025em",
    },
    h6: {
      fontWeight: 600,
      letterSpacing: "-0.025em",
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: "none",
          fontWeight: 600,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow:
            "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)",
        },
      },
    },
  },
};

export const createAppTheme = (themeName: ThemeName) => {
  switch (themeName) {
    case themeNames.LIGHT:
      return createTheme(lightThemeOptions);
    case themeNames.DARK:
      return createTheme(darkThemeOptions);
    case themeNames.NEXUS:
      return createTheme(nexusThemeOptions);
    case themeNames.MODERN_MINIMAL:
      return createTheme(lightThemeOptions);
    default:
      return createTheme(lightThemeOptions);
  }
};

export const themes = {
  [themeNames.LIGHT]: createTheme(lightThemeOptions),
  [themeNames.DARK]: createTheme(darkThemeOptions),
  [themeNames.NEXUS]: createTheme(nexusThemeOptions),
  [themeNames.MODERN_MINIMAL]: createTheme(lightThemeOptions), // Using light theme as base for now
};
