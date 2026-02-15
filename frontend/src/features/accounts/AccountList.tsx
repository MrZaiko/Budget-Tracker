import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  Skeleton,
  Typography,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { useAccounts } from './useAccounts';
import AccountDrawer from './AccountDrawer';
import EmptyState from '@/components/common/EmptyState';
import AmountDisplay from '@/components/common/AmountDisplay';
import type { Account } from '@/types/account';

const AccountCard: React.FC<{ account: Account; onClick: () => void }> = ({ account, onClick }) => (
  <Card
    sx={{ cursor: 'pointer', '&:hover': { borderColor: 'primary.main' } }}
    onClick={onClick}
  >
    <CardContent>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography variant="subtitle1" fontWeight={600}>
            {account.name}
          </Typography>
          <Chip
            label={account.type.replace('_', ' ')}
            size="small"
            sx={{ mt: 0.5 }}
          />
        </Box>
        <Box sx={{ textAlign: 'right' }}>
          <AmountDisplay
            amount={account.balance ?? account.initial_balance}
            currency={account.currency}
            variant="h6"
          />
          <Typography variant="caption" color="text.secondary">
            {account.currency}
          </Typography>
        </Box>
      </Box>
      {!account.is_active && (
        <Chip label="Inactive" color="default" size="small" sx={{ mt: 1 }} />
      )}
    </CardContent>
  </Card>
);

const AccountList: React.FC = () => {
  const { data: accounts, isLoading } = useAccounts();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selected, setSelected] = useState<Account | undefined>();

  const handleOpen = (account?: Account) => {
    setSelected(account);
    setDrawerOpen(true);
  };

  if (isLoading) {
    return (
      <Grid container spacing={2}>
        {[1, 2, 3].map((i) => (
          <Grid item xs={12} sm={6} md={4} key={i}>
            <Skeleton variant="rectangular" height={120} sx={{ borderRadius: 2 }} />
          </Grid>
        ))}
      </Grid>
    );
  }

  return (
    <>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpen()}
        >
          Add Account
        </Button>
      </Box>

      {!accounts?.length ? (
        <EmptyState
          title="No accounts yet"
          description="Add your first financial account to get started."
          actionLabel="Add Account"
          onAction={() => handleOpen()}
        />
      ) : (
        <Grid container spacing={2}>
          {accounts.map((account) => (
            <Grid item xs={12} sm={6} md={4} key={account.id}>
              <AccountCard account={account} onClick={() => handleOpen(account)} />
            </Grid>
          ))}
        </Grid>
      )}

      <AccountDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        account={selected}
      />
    </>
  );
};

export default AccountList;
