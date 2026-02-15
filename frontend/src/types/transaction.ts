export type TransactionType = 'income' | 'expense' | 'transfer';

export interface Transaction {
  id: string;
  user_id: string;
  account_id: string;
  category_id: string | null;
  budget_id: string | null;
  recurring_rule_id: string | null;
  type: TransactionType;
  amount: string;
  currency: string;
  account_currency: string | null;
  amount_account: string | null;
  account_exchange_rate: string | null;
  amount_base: string;
  exchange_rate: string;
  date: string;
  notes: string | null;
  transfer_to_account_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface TransactionCreate {
  account_id: string;
  category_id?: string | null;
  budget_id?: string | null;
  type: TransactionType;
  amount: string;
  currency: string;
  date: string;
  notes?: string | null;
  transfer_to_account_id?: string | null;
}

export interface TransactionUpdate {
  category_id?: string | null;
  budget_id?: string | null;
  amount?: string;
  date?: string;
  notes?: string | null;
}

export interface TransactionFilters {
  account_id?: string;
  category_id?: string;
  budget_id?: string;
  type?: TransactionType;
  from_date?: string;
  to_date?: string;
  currency?: string;
  page?: number;
  page_size?: number;
}
