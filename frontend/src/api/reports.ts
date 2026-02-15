import { apiClient } from './client';
import type {
  SpendingReport,
  IncomeVsExpenseReport,
  TrendsReport,
  NetWorthReport,
} from '@/types/reports';

interface ReportParams {
  from_date?: string;
  to_date?: string;
  currency?: string;
  months?: number;
}

export const getSpendingReport = async (params: ReportParams): Promise<SpendingReport> => {
  const { data } = await apiClient.get<SpendingReport>('/reports/spending', { params });
  return data;
};

export const getIncomeVsExpenseReport = async (
  params: ReportParams
): Promise<IncomeVsExpenseReport> => {
  const { data } = await apiClient.get<IncomeVsExpenseReport>('/reports/income-vs-expenses', {
    params,
  });
  return data;
};

export const getTrendsReport = async (params: ReportParams): Promise<TrendsReport> => {
  const { data } = await apiClient.get<TrendsReport>('/reports/trends', { params });
  return data;
};

export const getNetWorthReport = async (params: ReportParams): Promise<NetWorthReport> => {
  const { data } = await apiClient.get<NetWorthReport>('/reports/net-worth', { params });
  return data;
};
