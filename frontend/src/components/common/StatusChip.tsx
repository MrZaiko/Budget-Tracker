import React from 'react';
import { Chip } from '@mui/material';
import type { ChipProps } from '@mui/material';

type Status = 'active' | 'paused' | 'cancelled' | string;

const statusConfig: Record<string, { color: ChipProps['color']; label: string }> = {
  active: { color: 'success', label: 'Active' },
  paused: { color: 'warning', label: 'Paused' },
  cancelled: { color: 'default', label: 'Cancelled' },
};

interface Props {
  status: Status;
  size?: ChipProps['size'];
}

const StatusChip: React.FC<Props> = ({ status, size = 'small' }) => {
  const config = statusConfig[status] ?? { color: 'default' as ChipProps['color'], label: status };
  return <Chip label={config.label} color={config.color} size={size} />;
};

export default StatusChip;
