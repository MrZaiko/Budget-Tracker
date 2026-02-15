import React from 'react';
import { Box, Typography, TextField, Stack, InputAdornment } from '@mui/material';
import { useLocalStorage } from '@/hooks/useLocalStorage';

const NotificationsTab: React.FC = () => {
  const [leadTime, setLeadTime] = useLocalStorage<number>('notificationLeadTime', 7);

  return (
    <Box>
      <Typography variant="h6" gutterBottom>Notifications</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Configure when you receive subscription renewal alerts.
      </Typography>
      <Stack spacing={2} sx={{ maxWidth: 300 }}>
        <TextField
          label="Alert lead time"
          type="number"
          value={leadTime}
          onChange={(e) => setLeadTime(parseInt(e.target.value, 10) || 7)}
          inputProps={{ min: 1, max: 60 }}
          InputProps={{
            endAdornment: <InputAdornment position="end">days before</InputAdornment>,
          }}
          helperText="You'll be alerted this many days before a subscription renews."
          fullWidth
        />
      </Stack>
    </Box>
  );
};

export default NotificationsTab;
