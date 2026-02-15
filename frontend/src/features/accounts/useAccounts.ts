import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getAccounts, createAccount, updateAccount, deleteAccount } from '@/api/accounts';
import type { AccountCreate, AccountUpdate } from '@/types/account';
import { useSnackbarStore } from '@/stores/snackbarStore';

export const useAccounts = () =>
  useQuery({ queryKey: ['accounts'], queryFn: getAccounts });

export const useCreateAccount = () => {
  const qc = useQueryClient();
  const show = useSnackbarStore((s) => s.showSnackbar);
  return useMutation({
    mutationFn: (payload: AccountCreate) => createAccount(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['accounts'] });
      show('Account created', 'success');
    },
    onError: () => show('Failed to create account', 'error'),
  });
};

export const useUpdateAccount = () => {
  const qc = useQueryClient();
  const show = useSnackbarStore((s) => s.showSnackbar);
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: AccountUpdate }) =>
      updateAccount(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['accounts'] });
      show('Account updated', 'success');
    },
    onError: () => show('Failed to update account', 'error'),
  });
};

export const useDeleteAccount = () => {
  const qc = useQueryClient();
  const show = useSnackbarStore((s) => s.showSnackbar);
  return useMutation({
    mutationFn: (id: string) => deleteAccount(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['accounts'] });
      show('Account deleted', 'success');
    },
    onError: (error: unknown) => {
      const status = (error as { response?: { status?: number } })?.response?.status;
      if (status === 409) {
        show('Cannot delete: account has linked transactions', 'error');
      } else {
        show('Failed to delete account', 'error');
      }
    },
  });
};
