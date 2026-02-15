import { apiClient } from './client';
import type { Category, CategoryCreate, CategoryUpdate } from '@/types/category';

export const getCategories = async (): Promise<Category[]> => {
  const { data } = await apiClient.get<Category[]>('/categories');
  return data;
};

export const createCategory = async (payload: CategoryCreate): Promise<Category> => {
  const { data } = await apiClient.post<Category>('/categories', payload);
  return data;
};

export const updateCategory = async (id: string, payload: CategoryUpdate): Promise<Category> => {
  const { data } = await apiClient.patch<Category>(`/categories/${id}`, payload);
  return data;
};

export const deleteCategory = async (id: string): Promise<void> => {
  await apiClient.delete(`/categories/${id}`);
};
