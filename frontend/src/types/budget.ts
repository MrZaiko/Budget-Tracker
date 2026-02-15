export type BudgetPeriodType = 'monthly' | 'weekly' | 'yearly' | 'custom';
export type CollaboratorRole = 'viewer' | 'editor';

export interface BudgetCategory {
  id: string;
  budget_id: string;
  category_id: string;
  limit_amount: string;
}

export interface Budget {
  id: string;
  owner_id: string;
  name: string;
  period_type: BudgetPeriodType;
  start_date: string;
  end_date: string | null;
  currency: string;
  budget_categories: BudgetCategory[];
  created_at: string;
  updated_at: string;
}

export interface BudgetCreate {
  name: string;
  period_type: BudgetPeriodType;
  start_date: string;
  end_date?: string | null;
  currency: string;
  budget_categories?: { category_id: string; limit_amount: string }[];
}

export interface BudgetUpdate {
  name?: string;
  period_type?: BudgetPeriodType;
  start_date?: string;
  end_date?: string | null;
  currency?: string;
  budget_categories?: { category_id: string; limit_amount: string }[];
}

export interface Collaborator {
  id: string;
  budget_id: string;
  user_id: string;
  role: CollaboratorRole;
  invited_at: string;
  accepted_at: string | null;
}

export interface CollaboratorInvite {
  email: string;
  role?: CollaboratorRole;
}

export interface CollaboratorUpdate {
  role: CollaboratorRole;
}

export interface BudgetSummaryCategory {
  category_id: string;
  category_name: string;
  limit_amount: string;
  spent_amount: string;
  remaining: string;
}

export interface BudgetSummary {
  budget_id: string;
  budget_name: string;
  period_type: string;
  start_date: string;
  end_date: string | null;
  currency: string;
  categories: BudgetSummaryCategory[];
  total_limit: string;
  total_spent: string;
  total_remaining: string;
}
