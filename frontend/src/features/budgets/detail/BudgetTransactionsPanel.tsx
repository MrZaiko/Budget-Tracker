import React, { useState } from 'react';
import {
  Box,
  Chip,
  IconButton,
  Skeleton,
  Stack,
  Typography,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import { useTransactions } from '@/features/transactions/useTransactions';
import TransactionEditDrawer from '@/features/transactions/TransactionEditDrawer';
import AmountDisplay from '@/components/common/AmountDisplay';
import type { Transaction } from '@/types/transaction';

interface Props {
  budgetId: string;
  budgetCurrency: string;
}

const typeColor: Record<string, 'success' | 'error' | 'info'> = {
  income: 'success',
  expense: 'error',
  transfer: 'info',
};

/** Return the amount and currency to display for a transaction in the context of a budget.
 *  Prefer the account-currency converted amount when available, so all rows are
 *  shown in a consistent currency matching the account (and usually the budget). */
function resolveDisplay(tx: Transaction): { amount: string; currency: string } {
  if (tx.amount_account !== null && tx.account_currency !== null && tx.currency !== tx.account_currency) {
    return { amount: tx.amount_account, currency: tx.account_currency };
  }
  return { amount: tx.amount, currency: tx.currency };
}

const BudgetTransactionsPanel: React.FC<Props> = ({ budgetId, budgetCurrency }) => {
  const [editingTx, setEditingTx] = useState<Transaction | null>(null);
  const { data, isLoading } = useTransactions({ budget_id: budgetId, page_size: 100 });

  if (isLoading) return <Skeleton variant="rectangular" height={200} sx={{ borderRadius: 1 }} />;

  const items = data?.items ?? [];

  return (
    <>
      {items.length === 0 ? (
        <Typography variant="body2" color="text.secondary">
          No transactions linked to this budget.
        </Typography>
      ) : (
        <Stack divider={<Box sx={{ borderBottom: '1px solid', borderColor: 'divider' }} />}>
          {items.map((tx) => {
            const { amount, currency } = resolveDisplay(tx);
            return (
              <Box
                key={tx.id}
                sx={{ display: 'flex', alignItems: 'center', gap: 1, py: 0.75, px: 0.5 }}
              >
                <Typography variant="body2" color="text.secondary" sx={{ minWidth: 90, flexShrink: 0 }}>
                  {tx.date}
                </Typography>
                <Chip label={tx.type} color={typeColor[tx.type]} size="small" sx={{ flexShrink: 0 }} />
                <Typography variant="body2" noWrap sx={{ flex: 1, minWidth: 0 }}>
                  {tx.notes ?? ''}
                </Typography>
                <AmountDisplay
                  amount={amount}
                  currency={currency}
                  type={tx.type === 'transfer' ? 'neutral' : (tx.type as 'income' | 'expense')}
                  colorCoded
                  variant="body2"
                  sx={{ flexShrink: 0, textAlign: 'right' }}
                />
                <IconButton size="small" onClick={() => setEditingTx(tx)} sx={{ flexShrink: 0 }}>
                  <EditIcon fontSize="small" />
                </IconButton>
              </Box>
            );
          })}
        </Stack>
      )}
      <TransactionEditDrawer transaction={editingTx} onClose={() => setEditingTx(null)} />
    </>
  );
};

export default BudgetTransactionsPanel;
