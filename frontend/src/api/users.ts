import { apiClient } from './client';
import type { User, UserUpdate } from '@/types/user';

export const getCurrentUser = async (): Promise<User> => {
  const { data } = await apiClient.get<User>('/users/me');
  return data;
};

export const updateCurrentUser = async (payload: UserUpdate): Promise<User> => {
  const { data } = await apiClient.patch<User>('/users/me', payload);
  return data;
};

export const localLogin = async (
  email: string,
  password: string
): Promise<{ access_token: string }> => {
  const { data } = await apiClient.post<{ access_token: string }>('/auth/local/token', {
    email,
    password,
  });
  return data;
};
