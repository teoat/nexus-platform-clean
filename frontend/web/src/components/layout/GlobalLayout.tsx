/**
 * NEXUS Platform - Global Layout Component
 * Universal layout wrapper with header and footer for all pages
 */

import React, { ReactNode, useEffect, useState } from 'react';
import { Box, useTheme, useMediaQuery, Fade, Backdrop, CircularProgress } from '@mui/material';
import Header from './Header';
import Footer from './Footer';
import { useAuth } from '../../contexts/AuthContext';
import { useLocation } from 'react-router-dom';

interface GlobalLayoutProps {
  children: ReactNode;
}

const GlobalLayout: React.FC<GlobalLayoutProps> = ({ children }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { isLoading } = useAuth();
  const location = useLocation();
  const [pageLoading, setPageLoading] = useState(false);

  // Handle page transitions
  useEffect(() => {
    setPageLoading(true);
    const timer = setTimeout(() => {
      setPageLoading(false);
    }, 300);

    return () => clearTimeout(timer);
  }, [location.pathname]);

  // Show loading backdrop during authentication
  if (isLoading) {
    return (
      <Backdrop
        sx={{ 
          color: '#fff', 
          zIndex: theme.zIndex.drawer + 1,
          backgroundColor: 'rgba(0, 0, 0, 0.8)'
        }}
        open={true}
      >
        <Box sx={{ textAlign: 'center' }}>
          <CircularProgress color="inherit" size={60} />
          <Box sx={{ mt: 2 }}>
            <Box
              sx={{
                width: 40,
                height: 40,
                borderRadius: 2,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontWeight: 'bold',
                fontSize: '1.2rem',
                mx: 'auto',
                mb: 2
              }}
            >
              N
            </Box>
            <Box sx={{ color: 'white', fontSize: '1.1rem', fontWeight: 'bold' }}>
              NEXUS Platform
            </Box>
            <Box sx={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.9rem' }}>
              Forensic Financial Intelligence
            </Box>
          </Box>
        </Box>
      </Backdrop>
    );
  }

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        backgroundColor: theme.palette.background.default
      }}
    >
      {/* Header - Always visible */}
      <Header />

      {/* Main Content Area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          minHeight: 'calc(100vh - 64px)', // Adjust based on header height
          position: 'relative'
        }}
      >
        {/* Page Loading Overlay */}
        {pageLoading && (
          <Fade in={pageLoading}>
            <Box
              sx={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: 'rgba(255, 255, 255, 0.8)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: theme.zIndex.modal - 1,
                backdropFilter: 'blur(2px)'
              }}
            >
              <CircularProgress size={40} />
            </Box>
          </Fade>
        )}

        {/* Page Content */}
        <Fade in={!pageLoading} timeout={300}>
          <Box
            sx={{
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              opacity: pageLoading ? 0.3 : 1,
              transition: 'opacity 0.3s ease-in-out'
            }}
          >
            {children}
          </Box>
        </Fade>
      </Box>

      {/* Footer - Always visible */}
      <Footer />
    </Box>
  );
};

export default GlobalLayout;
