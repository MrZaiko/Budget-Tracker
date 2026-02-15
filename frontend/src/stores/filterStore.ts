import { create } from 'zustand';
import type { TransactionFilters } from '@/types/transaction';

interface FilterState {
  transactionFilters: TransactionFilters;
  setTransactionFilters: (filters: Partial<TransactionFilters>) => void;
  resetTransactionFilters: () => void;
}

const defaultFilters: TransactionFilters = {
  page: 1,
  page_size: 50,
};

export const useFilterStore = create<FilterState>((set) => ({
  transactionFilters: defaultFilters,
  setTransactionFilters: (filters) =>
    set((state) => ({
      transactionFilters: { ...state.transactionFilters, ...filters },
    })),
  resetTransactionFilters: () => set({ transactionFilters: defaultFilters }),
}));
