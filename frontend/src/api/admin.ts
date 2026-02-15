import { apiClient } from './client';
import type { User } from '@/types/user';
import type { Category, CategoryCreate, CategoryUpdate } from '@/types/category';

export const getAdminUsers = async (params?: { skip?: number; limit?: number }): Promise<User[]> => {
  const { data } = await apiClient.get<User[]>('/admin/users', { params });
  return data;
};

export const updateAdminUser = async (id: string, payload: { is_admin?: boolean }): Promise<User> => {
  const { data } = await apiClient.patch<User>(`/admin/users/${id}`, payload);
  return data;
};

export const deleteAdminUser = async (id: string): Promise<void> => {
  await apiClient.delete(`/admin/users/${id}`);
};

export const createSystemCategory = async (payload: CategoryCreate): Promise<Category> => {
  const { data } = await apiClient.post<Category>('/admin/categories', payload);
  return data;
};

export const updateSystemCategory = async (id: string, payload: CategoryUpdate): Promise<Category> => {
  const { data } = await apiClient.patch<Category>(`/admin/categories/${id}`, payload);
  return data;
};

export const deleteSystemCategory = async (id: string): Promise<void> => {
  await apiClient.delete(`/admin/categories/${id}`);
};
