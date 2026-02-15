export type RecurringFrequency = 'daily' | 'weekly' | 'monthly' | 'yearly';
export type RecurringStatus = 'active' | 'paused' | 'cancelled';

export interface RecurringRule {
  id: string;
  user_id: string;
  account_id: string;
  category_id: string | null;
  budget_id: string | null;
  name: string;
  type: 'income' | 'expense';
  amount: string;
  currency: string;
  frequency: RecurringFrequency;
  start_date: string;
  end_date: string | null;
  next_occurrence: string;
  is_subscription: boolean;
  status: RecurringStatus;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface RecurringRuleCreate {
  account_id: string;
  category_id?: string | null;
  budget_id?: string | null;
  name: string;
  type: 'income' | 'expense';
  amount: string;
  currency: string;
  frequency: RecurringFrequency;
  start_date: string;
  end_date?: string | null;
  is_subscription?: boolean;
  notes?: string | null;
}

export interface RecurringRuleUpdate {
  name?: string;
  amount?: string;
  category_id?: string | null;
  budget_id?: string | null;
  end_date?: string | null;
  is_subscription?: boolean;
  status?: RecurringStatus;
  notes?: string | null;
}

export interface UpcomingSubscription {
  id: string;
  name: string;
  amount: string;
  currency: string;
  next_occurrence: string;
  frequency: RecurringFrequency;
  days_until: number;
}
