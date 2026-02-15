import { apiClient } from './client';
import type { Currency, LatestRates, HistoricalRates } from '@/types/currency';

export const getCurrencies = async (): Promise<Currency[]> => {
  const { data } = await apiClient.get<Currency[]>('/currencies');
  return data;
};

export const getLatestRates = async (): Promise<LatestRates> => {
  const { data } = await apiClient.get<LatestRates>('/currencies/rates');
  return data;
};

export const getHistoricalRates = async (from: string, to: string): Promise<HistoricalRates> => {
  const { data } = await apiClient.get<HistoricalRates>('/currencies/rates/history', {
    params: { from_date: from, to_date: to },
  });
  return data;
};
