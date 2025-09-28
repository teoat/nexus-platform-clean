import React from "react";
import {
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
  Box,
} from "@mui/material";
import {
  Palette as PaletteIcon,
  LightMode as LightModeIcon,
  DarkMode as DarkModeIcon,
  Brush as BrushIcon,
  Visibility as GlassIcon,
  BugReport as CyberIcon,
} from "@mui/icons-material";
import { useTheme } from "../../contexts/ThemeContext";
import { themeNames } from "../../design-system/theme/themes";

const themeOptions = [
  {
    key: "MODERN_MINIMAL",
    label: "Modern Minimal",
    icon: <LightModeIcon />,
    description: "Clean and modern light theme",
  },
  {
    key: "DARK",
    label: "Dark Mode",
    icon: <DarkModeIcon />,
    description: "Dark theme for low-light environments",
  },
  {
    key: "LIGHT",
    label: "Light Mode",
    icon: <LightModeIcon />,
    description: "Clean light theme",
  },
  {
    key: "NEXUS",
    label: "Nexus Theme",
    icon: <BrushIcon />,
    description: "Custom Nexus design",
  },
];

const ThemeSwitcher: React.FC = () => {
  const { currentTheme, setTheme, toggleDarkMode, isDarkMode } = useTheme();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleThemeSelect = (themeKey: string) => {
    setTheme(themeKey as any);
    handleClose();
  };

  return (
    <Box>
      <Tooltip title="Toggle Dark Mode">
        <IconButton onClick={toggleDarkMode} color="inherit" sx={{ mr: 1 }}>
          {isDarkMode ? <LightModeIcon /> : <DarkModeIcon />}
        </IconButton>
      </Tooltip>

      <Tooltip title="Theme Options">
        <IconButton onClick={handleClick} color="inherit">
          <PaletteIcon />
        </IconButton>
      </Tooltip>

      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        PaperProps={{
          sx: {
            minWidth: 200,
            maxHeight: 300,
          },
        }}
      >
        {themeOptions.map((option) => (
          <MenuItem
            key={option.key}
            onClick={() => handleThemeSelect(option.key)}
            selected={currentTheme === option.key}
          >
            <ListItemIcon>{option.icon}</ListItemIcon>
            <ListItemText
              primary={option.label}
              secondary={option.description}
            />
          </MenuItem>
        ))}
      </Menu>
    </Box>
  );
};

export default ThemeSwitcher;
