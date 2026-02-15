import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Avatar,
  Menu,
  MenuItem,
  Tooltip,
  Box,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LightModeIcon from '@mui/icons-material/LightMode';
import { useNavigate } from 'react-router-dom';
import { useAuth } from 'react-oidc-context';
import { useUIStore } from '@/stores/uiStore';
import { useThemeMode } from '@/theme/ThemeProvider';
import { useLocalAuthStore } from '@/stores/localAuthStore';
import { isLocalAuthEnabled } from '@/lib/auth';

const DRAWER_WIDTH = 240;

interface Props {
  title: string;
}

const TopBar: React.FC<Props> = ({ title }) => {
  const { toggleSidebar } = useUIStore();
  const { mode, toggleTheme } = useThemeMode();
  const auth = useAuth();
  const navigate = useNavigate();
  const clearLocalToken = useLocalAuthStore((s) => s.clearToken);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleLogout = () => {
    setAnchorEl(null);
    if (isLocalAuthEnabled()) {
      clearLocalToken();
      navigate('/login/local');
    } else {
      auth.signoutRedirect();
    }
  };

  const userInitial =
    auth.user?.profile?.name?.[0]?.toUpperCase() ??
    auth.user?.profile?.email?.[0]?.toUpperCase() ??
    'U';

  return (
    <AppBar
      position="fixed"
      elevation={0}
      sx={{
        width: { md: `calc(100% - ${DRAWER_WIDTH}px)` },
        ml: { md: `${DRAWER_WIDTH}px` },
        borderBottom: 1,
        borderColor: 'divider',
        bgcolor: 'background.paper',
        color: 'text.primary',
      }}
    >
      <Toolbar>
        <IconButton
          edge="start"
          onClick={toggleSidebar}
          sx={{ mr: 2, display: { md: 'none' } }}
        >
          <MenuIcon />
        </IconButton>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }} fontWeight={600}>
          {title}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Tooltip title={mode === 'dark' ? 'Light mode' : 'Dark mode'}>
            <IconButton onClick={toggleTheme} size="small">
              {mode === 'dark' ? <LightModeIcon /> : <DarkModeIcon />}
            </IconButton>
          </Tooltip>
          <Tooltip title="Account">
            <IconButton onClick={(e) => setAnchorEl(e.currentTarget)} size="small">
              <Avatar sx={{ width: 32, height: 32, fontSize: 14 }}>{userInitial}</Avatar>
            </IconButton>
          </Tooltip>
        </Box>
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={() => setAnchorEl(null)}
          transformOrigin={{ horizontal: 'right', vertical: 'top' }}
          anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        >
          <MenuItem onClick={() => { setAnchorEl(null); navigate('/settings'); }}>
            Settings
          </MenuItem>
          <MenuItem onClick={handleLogout}>Logout</MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default TopBar;
