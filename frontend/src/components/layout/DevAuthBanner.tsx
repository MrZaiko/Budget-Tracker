import React from 'react';
import { Alert } from '@mui/material';
import { isLocalAuthEnabled } from '@/lib/auth';
import { useLocalAuthStore } from '@/stores/localAuthStore';

const DevAuthBanner: React.FC = () => {
  const token = useLocalAuthStore((s) => s.token);
  if (!isLocalAuthEnabled() || !token) return null;

  return (
    <Alert severity="warning" sx={{ borderRadius: 0, py: 0.5 }} icon={false}>
      <strong>Dev / Local Auth</strong> — SSO is bypassed. Not for production use.
    </Alert>
  );
};

export default DevAuthBanner;
