import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getAdminUsers, updateAdminUser, deleteAdminUser } from '@/api/admin';
import { useSnackbarStore } from '@/stores/snackbarStore';

export const useAdminUsers = () =>
  useQuery({ queryKey: ['admin', 'users'], queryFn: () => getAdminUsers() });

export const useUpdateAdminUser = () => {
  const qc = useQueryClient();
  const show = useSnackbarStore((s) => s.showSnackbar);
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: { is_admin?: boolean } }) =>
      updateAdminUser(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['admin', 'users'] });
      qc.invalidateQueries({ queryKey: ['currentUser'] });
      show('User updated', 'success');
    },
    onError: (error: unknown) => {
      const code = (error as { response?: { data?: { detail?: { code?: string } } } })?.response?.data?.detail?.code;
      if (code === 'self_demotion_not_allowed') {
        show('You cannot remove your own admin role', 'error');
      } else {
        show('Failed to update user', 'error');
      }
    },
  });
};

export const useDeleteAdminUser = () => {
  const qc = useQueryClient();
  const show = useSnackbarStore((s) => s.showSnackbar);
  return useMutation({
    mutationFn: (id: string) => deleteAdminUser(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['admin', 'users'] });
      show('User deleted', 'success');
    },
    onError: () => show('Failed to delete user', 'error'),
  });
};
