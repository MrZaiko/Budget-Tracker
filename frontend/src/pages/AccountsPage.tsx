import React from 'react';
import { Box, Typography } from '@mui/material';
import AccountList from '@/features/accounts/AccountList';
import { useAccounts } from '@/features/accounts/useAccounts';
import AmountDisplay from '@/components/common/AmountDisplay';

const AccountsPage: React.FC = () => {
  const { data: accounts = [] } = useAccounts();

  const totalBalance = accounts
    .filter((a) => a.is_active)
    .reduce((sum, a) => sum + parseFloat(a.balance ?? a.initial_balance), 0);

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="body2" color="text.secondary">Total Balance (active accounts)</Typography>
        <AmountDisplay amount={totalBalance} currency="USD" variant="h4" fontWeight={700} />
      </Box>
      <AccountList />
    </Box>
  );
};

export default AccountsPage;
