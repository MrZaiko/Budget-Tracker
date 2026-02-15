import React, { useState } from 'react';
import { Box, Tab, Tabs } from '@mui/material';
import ProfileTab from '@/features/settings/ProfileTab';
import CategoriesTab from '@/features/categories/CategoriesTab';
import NotificationsTab from '@/features/settings/NotificationsTab';

const SettingsPage: React.FC = () => {
  const [tab, setTab] = useState(0);

  return (
    <Box>
      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 3 }}>
        <Tab label="Profile" />
        <Tab label="Categories" />
        <Tab label="Notifications" />
      </Tabs>
      {tab === 0 && <ProfileTab />}
      {tab === 1 && <CategoriesTab />}
      {tab === 2 && <NotificationsTab />}
    </Box>
  );
};

export default SettingsPage;
