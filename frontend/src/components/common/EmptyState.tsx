import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import InboxIcon from '@mui/icons-material/Inbox';

interface Props {
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: React.ReactNode;
}

const EmptyState: React.FC<Props> = ({ title, description, actionLabel, onAction, icon }) => (
  <Box
    sx={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      py: 8,
      gap: 2,
      color: 'text.secondary',
    }}
  >
    {icon ?? <InboxIcon sx={{ fontSize: 56, opacity: 0.4 }} />}
    <Typography variant="h6" color="text.secondary">
      {title}
    </Typography>
    {description && (
      <Typography variant="body2" color="text.secondary" textAlign="center">
        {description}
      </Typography>
    )}
    {actionLabel && onAction && (
      <Button variant="contained" onClick={onAction} sx={{ mt: 1 }}>
        {actionLabel}
      </Button>
    )}
  </Box>
);

export default EmptyState;
