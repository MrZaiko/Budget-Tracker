import React, { useState } from 'react';
import { Box, Toolbar } from '@mui/material';
import { useLocation } from 'react-router-dom';
import Sidebar, { DRAWER_WIDTH } from './Sidebar';
import TopBar from './TopBar';
import BottomNav from './BottomNav';
import DevAuthBanner from './DevAuthBanner';
import NetworkErrorBanner from '@/components/common/NetworkErrorBanner';
import SnackbarHost from '@/components/common/SnackbarHost';

const PAGE_TITLES: Record<string, string> = {
  '/': 'Dashboard',
  '/accounts': 'Accounts',
  '/transactions': 'Transactions',
  '/budgets': 'Budgets',
  '/recurring': 'Recurring',
  '/subscriptions': 'Subscriptions',
  '/reports': 'Reports',
  '/settings': 'Settings',
};

interface Props {
  children: React.ReactNode;
}

const AppShell: React.FC<Props> = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  const title =
    PAGE_TITLES[location.pathname] ??
    (location.pathname.startsWith('/budgets/') ? 'Budget Detail' : 'Budget Tracker');

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar mobileOpen={mobileOpen} onClose={() => setMobileOpen(false)} />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { md: `calc(100% - ${DRAWER_WIDTH}px)` },
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <TopBar title={title} />
        <Toolbar />
        <DevAuthBanner />
        <NetworkErrorBanner />
        <Box sx={{ flexGrow: 1, p: { xs: 2, md: 3 }, pb: { xs: 10, md: 3 } }}>
          {children}
        </Box>
        <BottomNav />
        <SnackbarHost />
      </Box>
    </Box>
  );
};

export default AppShell;
