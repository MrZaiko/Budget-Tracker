import { apiClient } from './client';
import type { Account, AccountCreate, AccountUpdate } from '@/types/account';

export const getAccounts = async (): Promise<Account[]> => {
  const { data } = await apiClient.get<Account[]>('/accounts');
  return data;
};

export const getAccount = async (id: string): Promise<Account> => {
  const { data } = await apiClient.get<Account>(`/accounts/${id}`);
  return data;
};

export const createAccount = async (payload: AccountCreate): Promise<Account> => {
  const { data } = await apiClient.post<Account>('/accounts', payload);
  return data;
};

export const updateAccount = async (id: string, payload: AccountUpdate): Promise<Account> => {
  const { data } = await apiClient.patch<Account>(`/accounts/${id}`, payload);
  return data;
};

export const deleteAccount = async (id: string): Promise<void> => {
  await apiClient.delete(`/accounts/${id}`);
};
