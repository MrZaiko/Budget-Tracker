import React from 'react';
import { Typography } from '@mui/material';
import type { TypographyProps } from '@mui/material';

interface Props extends Omit<TypographyProps, 'children'> {
  amount: string | number;
  currency?: string;
  colorCoded?: boolean;
  type?: 'income' | 'expense' | 'neutral';
}

const AmountDisplay: React.FC<Props> = ({
  amount,
  currency = 'USD',
  colorCoded = false,
  type = 'neutral',
  ...typographyProps
}) => {
  const value = typeof amount === 'string' ? parseFloat(amount) : amount;
  const formatted = new Intl.NumberFormat(undefined, {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);

  const color = colorCoded
    ? type === 'income'
      ? 'success.main'
      : type === 'expense'
      ? 'error.main'
      : 'text.primary'
    : 'text.primary';

  return (
    <Typography color={color} {...typographyProps}>
      {formatted}
    </Typography>
  );
};

export default AmountDisplay;
