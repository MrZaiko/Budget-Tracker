import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getTransactions,
  createTransaction,
  updateTransaction,
  deleteTransaction,
  bulkDeleteTransactions,
} from '@/api/transactions';
import type { TransactionCreate, TransactionUpdate, TransactionFilters } from '@/types/transaction';
import { useSnackbarStore } from '@/stores/snackbarStore';

export const useTransactions = (filters: TransactionFilters = {}) =>
  useQuery({
    queryKey: ['transactions', filters],
    queryFn: () => getTransactions(filters),
  });

export const useCreateTransaction = () => {
  const qc = useQueryClient();
  const show = useSnackbarStore((s) => s.showSnackbar);
  return useMutation({
    mutationFn: (payload: TransactionCreate) => createTransaction(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['transactions'] });
      qc.invalidateQueries({ queryKey: ['accounts'] });
      show('Transaction created', 'success');
    },
    onError: () => show('Failed to create transaction', 'error'),
  });
};

export const useUpdateTransaction = () => {
  const qc = useQueryClient();
  const show = useSnackbarStore((s) => s.showSnackbar);
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: TransactionUpdate }) =>
      updateTransaction(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['transactions'] });
      qc.invalidateQueries({ queryKey: ['accounts'] });
      qc.invalidateQueries({ queryKey: ['budgets'] });
      show('Transaction updated', 'success');
    },
    onError: () => show('Failed to update transaction', 'error'),
  });
};

export const useDeleteTransaction = () => {
  const qc = useQueryClient();
  const show = useSnackbarStore((s) => s.showSnackbar);
  return useMutation({
    mutationFn: (id: string) => deleteTransaction(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['transactions'] });
      qc.invalidateQueries({ queryKey: ['accounts'] });
      qc.invalidateQueries({ queryKey: ['budgets'] });
      show('Transaction deleted', 'success');
    },
    onError: () => show('Failed to delete transaction', 'error'),
  });
};

export const useBulkDeleteTransactions = () => {
  const qc = useQueryClient();
  const show = useSnackbarStore((s) => s.showSnackbar);
  return useMutation({
    mutationFn: (ids: string[]) => bulkDeleteTransactions(ids),
    onSuccess: (_, ids) => {
      qc.invalidateQueries({ queryKey: ['transactions'] });
      qc.invalidateQueries({ queryKey: ['accounts'] });
      show(`${ids.length} transaction(s) deleted`, 'success');
    },
    onError: () => show('Failed to delete transactions', 'error'),
  });
};
