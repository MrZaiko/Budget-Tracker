import React from 'react';
import { Alert, Button } from '@mui/material';
import { useUIStore } from '@/stores/uiStore';
import { queryClient } from '@/lib/queryClient';

const NetworkErrorBanner: React.FC = () => {
  const hasNetworkError = useUIStore((s) => s.hasNetworkError);

  if (!hasNetworkError) return null;

  return (
    <Alert
      severity="error"
      sx={{ borderRadius: 0, position: 'sticky', top: 0, zIndex: 1300 }}
      action={
        <Button
          color="inherit"
          size="small"
          onClick={() => queryClient.refetchQueries()}
        >
          Retry
        </Button>
      }
    >
      Network error — check your connection and try again.
    </Alert>
  );
};

export default NetworkErrorBanner;
