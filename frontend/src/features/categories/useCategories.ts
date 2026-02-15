import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getCategories, createCategory, updateCategory, deleteCategory } from '@/api/categories';
import type { CategoryCreate, CategoryUpdate } from '@/types/category';
import { useSnackbarStore } from '@/stores/snackbarStore';

export const useCategories = () =>
  useQuery({ queryKey: ['categories'], queryFn: getCategories });

export const useCreateCategory = () => {
  const qc = useQueryClient();
  const show = useSnackbarStore((s) => s.showSnackbar);
  return useMutation({
    mutationFn: (payload: CategoryCreate) => createCategory(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['categories'] });
      show('Category created', 'success');
    },
    onError: () => show('Failed to create category', 'error'),
  });
};

export const useUpdateCategory = () => {
  const qc = useQueryClient();
  const show = useSnackbarStore((s) => s.showSnackbar);
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: CategoryUpdate }) =>
      updateCategory(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['categories'] });
      show('Category updated', 'success');
    },
    onError: () => show('Failed to update category', 'error'),
  });
};

export const useDeleteCategory = () => {
  const qc = useQueryClient();
  const show = useSnackbarStore((s) => s.showSnackbar);
  return useMutation({
    mutationFn: (id: string) => deleteCategory(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['categories'] });
      show('Category deleted', 'success');
    },
    onError: (error: unknown) => {
      const status = (error as { response?: { status?: number } })?.response?.status;
      if (status === 409) {
        show('Cannot delete: category has linked transactions', 'error');
      } else {
        show('Failed to delete category', 'error');
      }
    },
  });
};
