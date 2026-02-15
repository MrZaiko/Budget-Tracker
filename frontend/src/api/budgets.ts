import { apiClient } from './client';
import type {
  Budget,
  BudgetCreate,
  BudgetUpdate,
  BudgetSummary,
  Collaborator,
  CollaboratorInvite,
  CollaboratorUpdate,
} from '@/types/budget';

export const getBudgets = async (): Promise<Budget[]> => {
  const { data } = await apiClient.get<Budget[]>('/budgets');
  return data;
};

export const getBudget = async (id: string): Promise<Budget> => {
  const { data } = await apiClient.get<Budget>(`/budgets/${id}`);
  return data;
};

export const createBudget = async (payload: BudgetCreate): Promise<Budget> => {
  const { data } = await apiClient.post<Budget>('/budgets', payload);
  return data;
};

export const updateBudget = async (id: string, payload: BudgetUpdate): Promise<Budget> => {
  const { data } = await apiClient.patch<Budget>(`/budgets/${id}`, payload);
  return data;
};

export const deleteBudget = async (id: string): Promise<void> => {
  await apiClient.delete(`/budgets/${id}`);
};

export const getBudgetSummary = async (id: string): Promise<BudgetSummary> => {
  const { data } = await apiClient.get<BudgetSummary>(`/budgets/${id}/summary`);
  return data;
};

export const getCollaborators = async (budgetId: string): Promise<Collaborator[]> => {
  const { data } = await apiClient.get<Collaborator[]>(`/budgets/${budgetId}/collaborators`);
  return data;
};

export const inviteCollaborator = async (
  budgetId: string,
  payload: CollaboratorInvite
): Promise<Collaborator> => {
  const { data } = await apiClient.post<Collaborator>(
    `/budgets/${budgetId}/collaborators`,
    payload
  );
  return data;
};

export const updateCollaborator = async (
  budgetId: string,
  userId: string,
  payload: CollaboratorUpdate
): Promise<Collaborator> => {
  const { data } = await apiClient.patch<Collaborator>(
    `/budgets/${budgetId}/collaborators/${userId}`,
    payload
  );
  return data;
};

export const removeCollaborator = async (budgetId: string, userId: string): Promise<void> => {
  await apiClient.delete(`/budgets/${budgetId}/collaborators/${userId}`);
};
