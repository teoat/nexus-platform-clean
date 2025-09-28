import React, { useState } from "react";
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Paper,
  Container,
  AppBar,
  Toolbar,
  IconButton,
  Menu,
  MenuItem,
} from "@mui/material";
import {
  Menu as MenuIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  AccountCircle as AccountCircleIcon,
} from "@mui/icons-material";
import { MainControlDashboard } from "../components/dashboard/MainControlDashboard";
import { AIIntelligenceDashboard } from "../components/dashboard/AIIntelligenceDashboard";
import { UserExperienceDashboard } from "../components/dashboard/UserExperienceDashboard";

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({
  children,
  value,
  index,
  ...other
}) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`dashboard-tabpanel-${index}`}
      aria-labelledby={`dashboard-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
};

const Dashboard: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const isMenuOpen = Boolean(anchorEl);

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" color="primary">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            NEXUS Platform Dashboard
          </Typography>
          <IconButton
            size="large"
            edge="end"
            aria-label="account of current user"
            aria-controls="primary-search-account-menu"
            aria-haspopup="true"
            onClick={handleProfileMenuOpen}
            color="inherit"
          >
            <AccountCircleIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 2 }}>
        <Paper elevation={1} sx={{ width: "100%" }}>
          <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
            <Tabs
              value={tabValue}
              onChange={handleTabChange}
              aria-label="dashboard tabs"
              variant="fullWidth"
            >
              <Tab
                label="Main Control"
                id="dashboard-tab-0"
                aria-controls="dashboard-tabpanel-0"
              />
              <Tab
                label="AI Intelligence"
                id="dashboard-tab-1"
                aria-controls="dashboard-tabpanel-1"
              />
              <Tab
                label="User Experience"
                id="dashboard-tab-2"
                aria-controls="dashboard-tabpanel-2"
              />
            </Tabs>
          </Box>

          <TabPanel value={tabValue} index={0}>
            <MainControlDashboard />
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <AIIntelligenceDashboard />
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <UserExperienceDashboard />
          </TabPanel>
        </Paper>
      </Container>

      <Menu
        anchorEl={anchorEl}
        anchorOrigin={{
          vertical: "top",
          horizontal: "right",
        }}
        id="primary-search-account-menu"
        keepMounted
        transformOrigin={{
          vertical: "top",
          horizontal: "right",
        }}
        open={isMenuOpen}
        onClose={handleProfileMenuClose}
      >
        <MenuItem onClick={handleProfileMenuClose}>Profile</MenuItem>
        <MenuItem onClick={handleProfileMenuClose}>Settings</MenuItem>
        <MenuItem onClick={handleProfileMenuClose}>Logout</MenuItem>
      </Menu>
    </Box>
  );
};

export default Dashboard;
