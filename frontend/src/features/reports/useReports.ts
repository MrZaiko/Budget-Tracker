import { useQuery } from '@tanstack/react-query';
import {
  getSpendingReport,
  getIncomeVsExpenseReport,
  getTrendsReport,
  getNetWorthReport,
} from '@/api/reports';

interface ReportParams {
  from_date?: string;
  to_date?: string;
  currency?: string;
  months?: number;
}

export const useSpendingReport = (params: ReportParams) =>
  useQuery({
    queryKey: ['reports', 'spending', params],
    queryFn: () => getSpendingReport(params),
    enabled: !!(params.from_date && params.to_date),
  });

export const useIncomeVsExpenseReport = (params: ReportParams) =>
  useQuery({
    queryKey: ['reports', 'income-vs-expenses', params],
    queryFn: () => getIncomeVsExpenseReport(params),
    enabled: !!(params.from_date && params.to_date),
  });

export const useTrendsReport = (params: ReportParams) =>
  useQuery({
    queryKey: ['reports', 'trends', params],
    queryFn: () => getTrendsReport(params),
  });

export const useNetWorthReport = (params: ReportParams) =>
  useQuery({
    queryKey: ['reports', 'net-worth', params],
    queryFn: () => getNetWorthReport(params),
  });
