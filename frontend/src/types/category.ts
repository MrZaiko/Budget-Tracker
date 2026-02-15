export type TransactionTypeFilter = 'income' | 'expense' | 'both';

export interface Category {
  id: string;
  user_id: string | null;
  name: string;
  icon: string | null;
  color: string | null;
  transaction_type: TransactionTypeFilter;
  is_system: boolean;
  created_at: string;
  updated_at: string;
}

export interface CategoryCreate {
  name: string;
  icon?: string | null;
  color?: string | null;
  transaction_type?: TransactionTypeFilter;
}

export interface CategoryUpdate {
  name?: string;
  icon?: string | null;
  color?: string | null;
  transaction_type?: TransactionTypeFilter;
}
