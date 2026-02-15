import React from 'react';
import { Snackbar, Alert } from '@mui/material';
import { useSnackbarStore } from '@/stores/snackbarStore';

const SnackbarHost: React.FC = () => {
  const messages = useSnackbarStore((s) => s.messages);
  const dismiss = useSnackbarStore((s) => s.dismissSnackbar);

  return (
    <>
      {messages.map((msg) => (
        <Snackbar
          key={msg.id}
          open
          autoHideDuration={5000}
          onClose={() => dismiss(msg.id)}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert
            severity={msg.severity}
            onClose={() => dismiss(msg.id)}
            variant="filled"
            sx={{ width: '100%' }}
          >
            {msg.message}
          </Alert>
        </Snackbar>
      ))}
    </>
  );
};

export default SnackbarHost;
