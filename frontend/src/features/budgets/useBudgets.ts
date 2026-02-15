import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getBudgets,
  getBudget,
  createBudget,
  updateBudget,
  deleteBudget,
  getBudgetSummary,
  getCollaborators,
  inviteCollaborator,
  updateCollaborator,
  removeCollaborator,
} from '@/api/budgets';
import type { BudgetCreate, BudgetUpdate, CollaboratorInvite, CollaboratorUpdate } from '@/types/budget';
import { useSnackbarStore } from '@/stores/snackbarStore';

export const useBudgets = () =>
  useQuery({ queryKey: ['budgets'], queryFn: getBudgets });

export const useBudget = (id: string) =>
  useQuery({ queryKey: ['budgets', id], queryFn: () => getBudget(id) });

export const useBudgetSummary = (id: string) =>
  useQuery({ queryKey: ['budgets', id, 'summary'], queryFn: () => getBudgetSummary(id) });

export const useCollaborators = (budgetId: string) =>
  useQuery({
    queryKey: ['budgets', budgetId, 'collaborators'],
    queryFn: () => getCollaborators(budgetId),
  });

export const useCreateBudget = () => {
  const qc = useQueryClient();
  const show = useSnackbarStore((s) => s.showSnackbar);
  return useMutation({
    mutationFn: (payload: BudgetCreate) => createBudget(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['budgets'] });
      show('Budget created', 'success');
    },
    onError: () => show('Failed to create budget', 'error'),
  });
};

export const useUpdateBudget = () => {
  const qc = useQueryClient();
  const show = useSnackbarStore((s) => s.showSnackbar);
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: BudgetUpdate }) =>
      updateBudget(id, payload),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: ['budgets'] });
      qc.invalidateQueries({ queryKey: ['budgets', id] });
      show('Budget updated', 'success');
    },
    onError: () => show('Failed to update budget', 'error'),
  });
};

export const useDeleteBudget = () => {
  const qc = useQueryClient();
  const show = useSnackbarStore((s) => s.showSnackbar);
  return useMutation({
    mutationFn: (id: string) => deleteBudget(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['budgets'] });
      show('Budget deleted', 'success');
    },
    onError: () => show('Failed to delete budget', 'error'),
  });
};

export const useInviteCollaborator = (budgetId: string) => {
  const qc = useQueryClient();
  const show = useSnackbarStore((s) => s.showSnackbar);
  return useMutation({
    mutationFn: (payload: CollaboratorInvite) => inviteCollaborator(budgetId, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['budgets', budgetId, 'collaborators'] });
      show('Collaborator invited', 'success');
    },
    onError: () => show('Failed to invite collaborator', 'error'),
  });
};

export const useUpdateCollaborator = (budgetId: string) => {
  const qc = useQueryClient();
  const show = useSnackbarStore((s) => s.showSnackbar);
  return useMutation({
    mutationFn: ({ userId, payload }: { userId: string; payload: CollaboratorUpdate }) =>
      updateCollaborator(budgetId, userId, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['budgets', budgetId, 'collaborators'] });
      show('Role updated', 'success');
    },
    onError: () => show('Failed to update role', 'error'),
  });
};

export const useRemoveCollaborator = (budgetId: string) => {
  const qc = useQueryClient();
  const show = useSnackbarStore((s) => s.showSnackbar);
  return useMutation({
    mutationFn: (userId: string) => removeCollaborator(budgetId, userId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['budgets', budgetId, 'collaborators'] });
      show('Collaborator removed', 'success');
    },
    onError: () => show('Failed to remove collaborator', 'error'),
  });
};
