import React, { useState } from 'react';
import { Grid } from '@mui/material';
import {
  NetWorthWidget,
  BudgetStatusWidget,
  SpendingWidget,
  RecentTransactionsWidget,
  UpcomingSubscriptionsWidget,
} from '@/features/dashboard/DashboardWidgets';
import TransactionModal from '@/features/transactions/TransactionModal';

const DashboardPage: React.FC = () => {
  const [txModalOpen, setTxModalOpen] = useState(false);

  return (
    <>
      <Grid container spacing={3}>
        {/* Row 1: summary stats */}
        <Grid item xs={12} md={4}>
          <NetWorthWidget />
        </Grid>
        <Grid item xs={12} md={8}>
          <RecentTransactionsWidget onAdd={() => setTxModalOpen(true)} />
        </Grid>

        {/* Row 2: spending breakdowns */}
        <Grid item xs={12} md={6}>
          <SpendingWidget />
        </Grid>
        <Grid item xs={12} md={6}>
          <BudgetStatusWidget />
        </Grid>

        {/* Row 3: upcoming */}
        <Grid item xs={12}>
          <UpcomingSubscriptionsWidget />
        </Grid>
      </Grid>
      <TransactionModal open={txModalOpen} onClose={() => setTxModalOpen(false)} />
    </>
  );
};

export default DashboardPage;
