import React from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Divider,
  List,
  ListItem,
  ListItemText,
  LinearProgress,
  Skeleton,
  Stack,
  Typography,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { useQueries } from '@tanstack/react-query';
import { useAccounts } from '@/features/accounts/useAccounts';
import { useBudgets } from '@/features/budgets/useBudgets';
import { useTransactions } from '@/features/transactions/useTransactions';
import { useUpcomingSubscriptions } from '@/features/subscriptions/useSubscriptions';
import { useSpendingReport } from '@/features/reports/useReports';
import { getBudgetSummary } from '@/api/budgets';
import AmountDisplay from '@/components/common/AmountDisplay';
import SpendingPieChart from '@/components/charts/SpendingPieChart';
import type { BudgetSummary } from '@/types/budget';

const getFirstDay = () => {
  const d = new Date();
  d.setDate(1);
  return d.toISOString().split('T')[0];
};

const getToday = () => new Date().toISOString().split('T')[0];

const getBudgetColor = (pct: number): 'success' | 'warning' | 'error' => {
  if (pct < 0.75) return 'success';
  if (pct < 0.9) return 'warning';
  return 'error';
};

// ─── Net Worth ────────────────────────────────────────────────────────────────

export const NetWorthWidget: React.FC = () => {
  const { data: accounts = [], isLoading } = useAccounts();

  const total = accounts.reduce((sum, a) => {
    return sum + parseFloat(a.balance ?? a.initial_balance);
  }, 0);

  if (isLoading) return <Skeleton variant="rectangular" height={100} sx={{ borderRadius: 2 }} />;

  return (
    <Card>
      <CardContent>
        <Typography variant="subtitle2" color="text.secondary">Net Worth</Typography>
        <Typography variant="h4" fontWeight={700}>{total.toFixed(2)}</Typography>
        <Typography variant="caption" color="text.secondary">{accounts.length} accounts</Typography>
      </CardContent>
    </Card>
  );
};

// ─── Spending by Budget ───────────────────────────────────────────────────────

export const BudgetStatusWidget: React.FC = () => {
  const { data: budgets = [], isLoading: budgetsLoading } = useBudgets();

  const summaryResults = useQueries({
    queries: budgets.map((b) => ({
      queryKey: ['budgets', b.id, 'summary'],
      queryFn: () => getBudgetSummary(b.id),
    })),
  });

  const isLoading = budgetsLoading || summaryResults.some((r) => r.isLoading);

  if (isLoading) return <Skeleton variant="rectangular" height={200} sx={{ borderRadius: 2 }} />;

  const summaries = summaryResults
    .map((r) => r.data)
    .filter((s): s is BudgetSummary => !!s);

  return (
    <Card>
      <CardContent>
        <Typography variant="subtitle1" fontWeight={600} gutterBottom>
          Spending by Budget
        </Typography>
        {summaries.length === 0 ? (
          <Typography variant="body2" color="text.secondary">No budgets set.</Typography>
        ) : (
          <Stack spacing={2} divider={<Divider />}>
            {summaries.map((s) => {
              const spent = parseFloat(s.total_spent);
              const limit = parseFloat(s.total_limit);
              const hasLimit = limit > 0;
              const pct = hasLimit ? Math.min(spent / limit, 1) : 0;
              const color = hasLimit ? getBudgetColor(pct) : 'info';

              return (
                <Box key={s.budget_id}>
                  {/* Header row */}
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2" fontWeight={500}>{s.budget_name}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {hasLimit
                        ? `${spent.toFixed(2)} / ${limit.toFixed(2)} ${s.currency}`
                        : `${spent.toFixed(2)} ${s.currency} spent`}
                    </Typography>
                  </Box>

                  {/* Progress bar */}
                  {hasLimit && (
                    <LinearProgress
                      variant="determinate"
                      value={pct * 100}
                      color={color as 'success' | 'warning' | 'error'}
                      sx={{ height: 8, borderRadius: 4, mb: 0.75 }}
                    />
                  )}

                  {/* Per-category breakdown */}
                  {s.categories.length > 0 && (
                    <Stack spacing={0.25} sx={{ pl: 1 }}>
                      {s.categories.map((c) => {
                        const catSpent = parseFloat(c.spent_amount);
                        const catLimit = parseFloat(c.limit_amount);
                        const catHasLimit = catLimit > 0;
                        const catPct = catHasLimit ? Math.min(catSpent / catLimit, 1) : 0;
                        return (
                          <Box
                            key={c.category_id}
                            sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                          >
                            <Typography variant="caption" color="text.secondary" sx={{ minWidth: 120 }}>
                              {c.category_name}
                            </Typography>
                            <Box sx={{ flex: 1, mx: 1.5 }}>
                              {catHasLimit && (
                                <LinearProgress
                                  variant="determinate"
                                  value={catPct * 100}
                                  color={getBudgetColor(catPct)}
                                  sx={{ height: 4, borderRadius: 2 }}
                                />
                              )}
                            </Box>
                            <Typography variant="caption" color="text.secondary" sx={{ textAlign: 'right', minWidth: 80 }}>
                              {catHasLimit
                                ? `${catSpent.toFixed(2)} / ${catLimit.toFixed(2)}`
                                : catSpent.toFixed(2)}
                            </Typography>
                          </Box>
                        );
                      })}
                    </Stack>
                  )}
                </Box>
              );
            })}
          </Stack>
        )}
      </CardContent>
    </Card>
  );
};

// ─── Spending by Category ─────────────────────────────────────────────────────

export const SpendingWidget: React.FC = () => {
  const { data: report, isLoading } = useSpendingReport({
    from_date: getFirstDay(),
    to_date: getToday(),
  });

  if (isLoading) return <Skeleton variant="rectangular" height={300} sx={{ borderRadius: 2 }} />;

  if (!report || report.categories.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="subtitle1" fontWeight={600}>Spending by Category</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            No spending data for this month.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const total = parseFloat(report.total);

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', mb: 1 }}>
          <Typography variant="subtitle1" fontWeight={600}>Spending by Category</Typography>
          <Typography variant="body2" color="text.secondary">
            {report.currency} {total.toFixed(2)} this month
          </Typography>
        </Box>

        <SpendingPieChart categories={report.categories} />

        <Divider sx={{ my: 1.5 }} />

        {/* Sorted breakdown list */}
        <Stack spacing={1}>
          {report.categories.map((c) => {
            const amount = parseFloat(c.amount);
            const pct = parseFloat(c.percentage);
            return (
              <Box key={c.category_id ?? 'uncategorized'}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.25 }}>
                  <Typography variant="body2">{c.category_name}</Typography>
                  <Typography variant="body2" fontWeight={500} color="error.main">
                    {amount.toFixed(2)} {report.currency}
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={Math.min(pct, 100)}
                  color="error"
                  sx={{ height: 4, borderRadius: 2, opacity: 0.6 }}
                />
              </Box>
            );
          })}
        </Stack>
      </CardContent>
    </Card>
  );
};

// ─── Recent Transactions ──────────────────────────────────────────────────────

export const RecentTransactionsWidget: React.FC<{ onAdd: () => void }> = ({ onAdd }) => {
  const { data, isLoading } = useTransactions({ page: 1, page_size: 5 });

  if (isLoading) return <Skeleton variant="rectangular" height={200} sx={{ borderRadius: 2 }} />;

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="subtitle1" fontWeight={600}>Recent Transactions</Typography>
          <Button size="small" startIcon={<AddIcon />} onClick={onAdd}>Add</Button>
        </Box>
        {!data?.items.length ? (
          <Typography variant="body2" color="text.secondary">No transactions yet.</Typography>
        ) : (
          <List dense>
            {data.items.map((tx) => (
              <ListItem key={tx.id} disablePadding>
                <ListItemText
                  primary={tx.notes ?? tx.type}
                  secondary={tx.date}
                />
                <AmountDisplay
                  amount={tx.amount}
                  currency={tx.currency}
                  type={tx.type === 'transfer' ? 'neutral' : tx.type as 'income' | 'expense'}
                  colorCoded
                  variant="body2"
                />
              </ListItem>
            ))}
          </List>
        )}
      </CardContent>
    </Card>
  );
};

// ─── Upcoming Subscriptions ───────────────────────────────────────────────────

export const UpcomingSubscriptionsWidget: React.FC = () => {
  const { data: upcoming = [], isLoading } = useUpcomingSubscriptions(30);

  if (isLoading) return <Skeleton variant="rectangular" height={150} sx={{ borderRadius: 2 }} />;

  return (
    <Card>
      <CardContent>
        <Typography variant="subtitle1" fontWeight={600} gutterBottom>Upcoming Subscriptions</Typography>
        {upcoming.length === 0 ? (
          <Typography variant="body2" color="text.secondary">No renewals in next 30 days.</Typography>
        ) : (
          <List dense>
            {upcoming.slice(0, 5).map((item) => (
              <ListItem key={item.id} disablePadding>
                <ListItemText
                  primary={item.name}
                  secondary={`${item.next_occurrence} (${item.days_until}d)`}
                />
                <AmountDisplay amount={item.amount} currency={item.currency} variant="body2" />
              </ListItem>
            ))}
          </List>
        )}
      </CardContent>
    </Card>
  );
};
