import { apiClient } from './client';
import type {
  RecurringRule,
  RecurringRuleCreate,
  RecurringRuleUpdate,
  UpcomingSubscription,
} from '@/types/recurring';

export const getRecurringRules = async (): Promise<RecurringRule[]> => {
  const { data } = await apiClient.get<RecurringRule[]>('/recurring');
  return data;
};

export const getRecurringRule = async (id: string): Promise<RecurringRule> => {
  const { data } = await apiClient.get<RecurringRule>(`/recurring/${id}`);
  return data;
};

export const createRecurringRule = async (payload: RecurringRuleCreate): Promise<RecurringRule> => {
  const { data } = await apiClient.post<RecurringRule>('/recurring', payload);
  return data;
};

export const updateRecurringRule = async (
  id: string,
  payload: RecurringRuleUpdate
): Promise<RecurringRule> => {
  const { data } = await apiClient.patch<RecurringRule>(`/recurring/${id}`, payload);
  return data;
};

export const deleteRecurringRule = async (id: string): Promise<void> => {
  await apiClient.delete(`/recurring/${id}`);
};

export const getSubscriptions = async (): Promise<RecurringRule[]> => {
  const { data } = await apiClient.get<RecurringRule[]>('/subscriptions');
  return data;
};

export const getUpcomingSubscriptions = async (days = 30): Promise<UpcomingSubscription[]> => {
  const { data } = await apiClient.get<UpcomingSubscription[]>('/subscriptions/upcoming', {
    params: { days },
  });
  return data;
};
