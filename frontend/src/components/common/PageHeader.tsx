import React from 'react';
import { Box, Typography, Divider } from '@mui/material';

interface Props {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
}

const PageHeader: React.FC<Props> = ({ title, subtitle, action }) => (
  <Box>
    <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 1 }}>
      <Box>
        <Typography variant="h5" fontWeight={600}>
          {title}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="text.secondary" mt={0.5}>
            {subtitle}
          </Typography>
        )}
      </Box>
      {action && <Box>{action}</Box>}
    </Box>
    <Divider sx={{ mt: 1, mb: 3 }} />
  </Box>
);

export default PageHeader;
