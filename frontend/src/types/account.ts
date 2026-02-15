export const ACCOUNT_TYPES = ['checking', 'savings', 'credit_card', 'cash', 'other'] as const;
export type AccountType = typeof ACCOUNT_TYPES[number];

export interface Account {
  id: string;
  user_id: string;
  name: string;
  type: AccountType;
  currency: string;
  initial_balance: string;
  is_active: boolean;
  balance: string | null;
  created_at: string;
  updated_at: string;
}

export interface AccountCreate {
  name: string;
  type: AccountType;
  currency: string;
  initial_balance?: string;
  is_active?: boolean;
}

export interface AccountUpdate {
  name?: string;
  type?: AccountType;
  is_active?: boolean;
}
