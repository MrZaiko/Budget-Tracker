import { apiClient } from './client';
import type { Transaction, TransactionCreate, TransactionUpdate, TransactionFilters } from '@/types/transaction';
import type { PaginatedResponse } from '@/types/api';

export const getTransactions = async (
  filters: TransactionFilters = {}
): Promise<PaginatedResponse<Transaction>> => {
  const params = Object.fromEntries(
    Object.entries(filters).filter(([, v]) => v !== undefined && v !== null && v !== '')
  );
  const { data } = await apiClient.get<PaginatedResponse<Transaction>>('/transactions', { params });
  return data;
};

export const getTransaction = async (id: string): Promise<Transaction> => {
  const { data } = await apiClient.get<Transaction>(`/transactions/${id}`);
  return data;
};

export const createTransaction = async (payload: TransactionCreate): Promise<Transaction> => {
  const { data } = await apiClient.post<Transaction>('/transactions', payload);
  return data;
};

export const updateTransaction = async (
  id: string,
  payload: TransactionUpdate
): Promise<Transaction> => {
  const { data } = await apiClient.patch<Transaction>(`/transactions/${id}`, payload);
  return data;
};

export const deleteTransaction = async (id: string): Promise<void> => {
  await apiClient.delete(`/transactions/${id}`);
};

export const bulkDeleteTransactions = async (ids: string[]): Promise<void> => {
  await Promise.all(ids.map((id) => apiClient.delete(`/transactions/${id}`)));
};
