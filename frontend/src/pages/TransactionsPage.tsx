import React, { useState } from 'react';
import { Box, Button } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import FilterPanel from '@/features/transactions/FilterPanel';
import TransactionTable from '@/features/transactions/TransactionTable';
import TransactionModal from '@/features/transactions/TransactionModal';
import TransactionEditDrawer from '@/features/transactions/TransactionEditDrawer';
import { useTransactions } from '@/features/transactions/useTransactions';
import { useFilterStore } from '@/stores/filterStore';
import type { Transaction } from '@/types/transaction';

const TransactionsPage: React.FC = () => {
  const [modalOpen, setModalOpen] = useState(false);
  const [editingTx, setEditingTx] = useState<Transaction | null>(null);
  const { transactionFilters } = useFilterStore();
  const { data, isLoading } = useTransactions(transactionFilters);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setModalOpen(true)}>
          Add Transaction
        </Button>
      </Box>
      <FilterPanel />
      <TransactionTable
        transactions={data?.items ?? []}
        total={data?.total ?? 0}
        page={transactionFilters.page ?? 1}
        pageSize={transactionFilters.page_size ?? 50}
        loading={isLoading}
        onEdit={setEditingTx}
      />
      <TransactionModal open={modalOpen} onClose={() => setModalOpen(false)} />
      <TransactionEditDrawer
        transaction={editingTx}
        onClose={() => setEditingTx(null)}
      />
    </Box>
  );
};

export default TransactionsPage;
