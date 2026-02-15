export interface SpendingByCategory {
  category_id: string | null;
  category_name: string;
  amount: string;
  percentage: string;
}

export interface SpendingReport {
  from_date: string;
  to_date: string;
  currency: string;
  total: string;
  categories: SpendingByCategory[];
}

export interface IncomeVsExpensePeriod {
  period: string;
  income: string;
  expenses: string;
  net: string;
}

export interface IncomeVsExpenseReport {
  from_date: string;
  to_date: string;
  currency: string;
  periods: IncomeVsExpensePeriod[];
  total_income: string;
  total_expenses: string;
  total_net: string;
}

export interface MonthlyTrend {
  month: string;
  income: string;
  expenses: string;
  net: string;
}

export interface TrendsReport {
  months: number;
  currency: string;
  trends: MonthlyTrend[];
}

export interface AccountBalance {
  account_id: string;
  account_name: string;
  account_type: string;
  currency: string;
  balance: string;
  balance_base: string;
}

export interface NetWorthReport {
  currency: string;
  date: string;
  accounts: AccountBalance[];
  total_assets: string;
  total_liabilities: string;
  net_worth: string;
}
