import React from 'react';
import { Box, TextField, MenuItem, Button, Stack } from '@mui/material';
import { useAccounts } from '@/features/accounts/useAccounts';
import { useCategories } from '@/features/categories/useCategories';
import { useFilterStore } from '@/stores/filterStore';
import type { TransactionType } from '@/types/transaction';

const FilterPanel: React.FC = () => {
  const { transactionFilters, setTransactionFilters, resetTransactionFilters } = useFilterStore();
  const { data: accounts = [] } = useAccounts();
  const { data: categories = [] } = useCategories();

  return (
    <Box sx={{ mb: 2 }}>
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} flexWrap="wrap">
        <TextField
          label="From"
          type="date"
          size="small"
          InputLabelProps={{ shrink: true }}
          value={transactionFilters.from_date ?? ''}
          onChange={(e) => setTransactionFilters({ from_date: e.target.value || undefined, page: 1 })}
          sx={{ minWidth: 140 }}
        />
        <TextField
          label="To"
          type="date"
          size="small"
          InputLabelProps={{ shrink: true }}
          value={transactionFilters.to_date ?? ''}
          onChange={(e) => setTransactionFilters({ to_date: e.target.value || undefined, page: 1 })}
          sx={{ minWidth: 140 }}
        />
        <TextField
          select
          label="Account"
          size="small"
          value={transactionFilters.account_id ?? ''}
          onChange={(e) => setTransactionFilters({ account_id: e.target.value || undefined, page: 1 })}
          sx={{ minWidth: 160 }}
        >
          <MenuItem value="">All accounts</MenuItem>
          {accounts.map((a) => <MenuItem key={a.id} value={a.id}>{a.name}</MenuItem>)}
        </TextField>
        <TextField
          select
          label="Category"
          size="small"
          value={transactionFilters.category_id ?? ''}
          onChange={(e) => setTransactionFilters({ category_id: e.target.value || undefined, page: 1 })}
          sx={{ minWidth: 160 }}
        >
          <MenuItem value="">All categories</MenuItem>
          {categories.map((c) => <MenuItem key={c.id} value={c.id}>{c.name}</MenuItem>)}
        </TextField>
        <TextField
          select
          label="Type"
          size="small"
          value={transactionFilters.type ?? ''}
          onChange={(e) =>
            setTransactionFilters({ type: (e.target.value as TransactionType) || undefined, page: 1 })
          }
          sx={{ minWidth: 130 }}
        >
          <MenuItem value="">All types</MenuItem>
          <MenuItem value="income">Income</MenuItem>
          <MenuItem value="expense">Expense</MenuItem>
          <MenuItem value="transfer">Transfer</MenuItem>
        </TextField>
        <Button size="small" onClick={resetTransactionFilters} variant="outlined">
          Reset
        </Button>
      </Stack>
    </Box>
  );
};

export default FilterPanel;
