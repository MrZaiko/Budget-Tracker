import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getRecurringRules,
  createRecurringRule,
  updateRecurringRule,
  deleteRecurringRule,
} from '@/api/recurring';
import type { RecurringRuleCreate, RecurringRuleUpdate } from '@/types/recurring';
import { useSnackbarStore } from '@/stores/snackbarStore';

export const useRecurringRules = () =>
  useQuery({ queryKey: ['recurring'], queryFn: getRecurringRules });

export const useCreateRecurringRule = () => {
  const qc = useQueryClient();
  const show = useSnackbarStore((s) => s.showSnackbar);
  return useMutation({
    mutationFn: (payload: RecurringRuleCreate) => createRecurringRule(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['recurring'] });
      show('Recurring rule created', 'success');
    },
    onError: () => show('Failed to create rule', 'error'),
  });
};

export const useUpdateRecurringRule = () => {
  const qc = useQueryClient();
  const show = useSnackbarStore((s) => s.showSnackbar);
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: RecurringRuleUpdate }) =>
      updateRecurringRule(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['recurring'] });
      show('Rule updated', 'success');
    },
    onError: () => show('Failed to update rule', 'error'),
  });
};

export const useDeleteRecurringRule = () => {
  const qc = useQueryClient();
  const show = useSnackbarStore((s) => s.showSnackbar);
  return useMutation({
    mutationFn: (id: string) => deleteRecurringRule(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['recurring'] });
      show('Rule deleted', 'success');
    },
    onError: () => show('Failed to delete rule', 'error'),
  });
};

export const usePauseResumeRule = () => {
  const qc = useQueryClient();
  const show = useSnackbarStore((s) => s.showSnackbar);
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: 'active' | 'paused' }) =>
      updateRecurringRule(id, { status }),
    onMutate: async ({ id, status }) => {
      await qc.cancelQueries({ queryKey: ['recurring'] });
      const prev = qc.getQueryData<ReturnType<typeof getRecurringRules>>(['recurring']);
      qc.setQueryData(['recurring'], (old: unknown) => {
        if (!Array.isArray(old)) return old;
        return old.map((r: { id: string; status: string }) =>
          r.id === id ? { ...r, status } : r
        );
      });
      return { prev };
    },
    onError: (_err, _vars, context) => {
      qc.setQueryData(['recurring'], (context as { prev: unknown })?.prev);
      show('Failed to update status', 'error');
    },
    onSettled: () => qc.invalidateQueries({ queryKey: ['recurring'] }),
  });
};
