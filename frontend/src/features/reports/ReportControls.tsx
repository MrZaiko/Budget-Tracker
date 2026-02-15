import React from 'react';
import { Box, TextField, Stack } from '@mui/material';

interface ReportParams {
  from_date: string;
  to_date: string;
}

interface Props {
  params: ReportParams;
  onChange: (params: ReportParams) => void;
}

const ReportControls: React.FC<Props> = ({ params, onChange }) => (
  <Box sx={{ mb: 3 }}>
    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
      <TextField
        label="From"
        type="date"
        size="small"
        InputLabelProps={{ shrink: true }}
        value={params.from_date}
        onChange={(e) => onChange({ ...params, from_date: e.target.value })}
        sx={{ minWidth: 150 }}
      />
      <TextField
        label="To"
        type="date"
        size="small"
        InputLabelProps={{ shrink: true }}
        value={params.to_date}
        onChange={(e) => onChange({ ...params, to_date: e.target.value })}
        sx={{ minWidth: 150 }}
      />
    </Stack>
  </Box>
);

export default ReportControls;
