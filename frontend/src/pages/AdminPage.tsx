import React from 'react';
import { Box, Typography } from '@mui/material';
import AdminUsersPanel from '@/features/admin/AdminUsersPanel';

const AdminPage: React.FC = () => (
  <Box>
    <Typography variant="h5" fontWeight={700} gutterBottom>
      Admin
    </Typography>
    <AdminUsersPanel />
  </Box>
);

export default AdminPage;
