import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  Dialog,
  DialogContent,
  DialogTitle,
  Grid,
  IconButton,
  LinearProgress,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import EditIcon from '@mui/icons-material/Edit';
import CloseIcon from '@mui/icons-material/Close';
import { useBudget, useBudgetSummary, useUpdateBudget } from '@/features/budgets/useBudgets';
import CollaboratorsPanel from '@/features/budgets/detail/CollaboratorsPanel';
import BudgetTransactionsPanel from '@/features/budgets/detail/BudgetTransactionsPanel';
import BudgetForm from '@/features/budgets/BudgetForm';
import AmountDisplay from '@/components/common/AmountDisplay';
import { useQuery } from '@tanstack/react-query';
import { getCurrentUser } from '@/api/users';

const getBudgetColor = (pct: number): 'success' | 'warning' | 'error' => {
  if (pct < 0.75) return 'success';
  if (pct < 0.9) return 'warning';
  return 'error';
};

const BudgetDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [editOpen, setEditOpen] = useState(false);
  const { data: budget, isLoading: budgetLoading } = useBudget(id!);
  const { data: summary, isLoading: summaryLoading } = useBudgetSummary(id!);
  const { data: currentUser } = useQuery({ queryKey: ['currentUser'], queryFn: getCurrentUser });
  const updateMutation = useUpdateBudget();

  const isOwner = budget?.owner_id === currentUser?.id;
  const totalPct =
    summary && parseFloat(summary.total_limit) > 0
      ? parseFloat(summary.total_spent) / parseFloat(summary.total_limit)
      : 0;

  if (budgetLoading || summaryLoading) {
    return (
      <Box>
        <Skeleton variant="rectangular" height={120} sx={{ mb: 2, borderRadius: 2 }} />
        <Skeleton variant="rectangular" height={300} sx={{ borderRadius: 2 }} />
      </Box>
    );
  }

  if (!budget) return <Typography>Budget not found.</Typography>;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/budgets')}>
          Back to Budgets
        </Button>
        {isOwner && (
          <Button startIcon={<EditIcon />} variant="outlined" onClick={() => setEditOpen(true)}>
            Edit Budget
          </Button>
        )}
      </Box>

      {/* Summary header */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h5" fontWeight={700} gutterBottom>{budget.name}</Typography>
          <Typography variant="body2" color="text.secondary">
            {budget.period_type} · {budget.start_date}
            {budget.end_date ? ` → ${budget.end_date}` : ''}
          </Typography>
          {summary && (
            <Box sx={{ mt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Typography variant="caption" color="text.secondary">Limit</Typography>
                  <AmountDisplay amount={summary.total_limit} currency={budget.currency} variant="h6" />
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="caption" color="text.secondary">Spent</Typography>
                  <AmountDisplay amount={summary.total_spent} currency={budget.currency} variant="h6" />
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="caption" color="text.secondary">Remaining</Typography>
                  <AmountDisplay amount={summary.total_remaining} currency={budget.currency} variant="h6" />
                </Grid>
              </Grid>
              <Box sx={{ mt: 2 }}>
                <LinearProgress
                  variant="determinate"
                  value={Math.min(totalPct * 100, 100)}
                  color={getBudgetColor(totalPct)}
                  sx={{ height: 10, borderRadius: 5 }}
                />
                <Typography variant="caption" color="text.secondary">
                  {(totalPct * 100).toFixed(0)}% of budget used
                </Typography>
              </Box>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Category breakdown */}
      {summary && summary.categories.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>Category Breakdown</Typography>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Category</TableCell>
                  <TableCell align="right">Limit</TableCell>
                  <TableCell align="right">Spent</TableCell>
                  <TableCell align="right">Remaining</TableCell>
                  <TableCell></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {summary.categories.map((cat) => {
                  const catPct =
                    parseFloat(cat.limit_amount) > 0
                      ? parseFloat(cat.spent_amount) / parseFloat(cat.limit_amount)
                      : 0;
                  return (
                    <TableRow key={cat.category_id}>
                      <TableCell>{cat.category_name}</TableCell>
                      <TableCell align="right">
                        <AmountDisplay amount={cat.limit_amount} currency={budget.currency} variant="body2" />
                      </TableCell>
                      <TableCell align="right">
                        <AmountDisplay amount={cat.spent_amount} currency={budget.currency} variant="body2" />
                      </TableCell>
                      <TableCell align="right">
                        <AmountDisplay amount={cat.remaining} currency={budget.currency} variant="body2" />
                      </TableCell>
                      <TableCell sx={{ width: 100 }}>
                        <LinearProgress
                          variant="determinate"
                          value={Math.min(catPct * 100, 100)}
                          color={getBudgetColor(catPct)}
                          sx={{ height: 6, borderRadius: 3 }}
                        />
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {/* Linked transactions */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Transactions</Typography>
          <BudgetTransactionsPanel budgetId={id!} budgetCurrency={budget.currency} />
        </CardContent>
      </Card>

      {/* Collaborators (owner only) */}
      {isOwner && (
        <Card>
          <CardContent>
            <CollaboratorsPanel budgetId={id!} />
          </CardContent>
        </Card>
      )}

      {/* Edit dialog */}
      <Dialog open={editOpen} onClose={() => setEditOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          Edit Budget
          <IconButton onClick={() => setEditOpen(false)} size="small"><CloseIcon /></IconButton>
        </DialogTitle>
        <DialogContent>
          {budget && (
            <BudgetForm
              budget={budget}
              onSubmit={(data) =>
                updateMutation.mutate(
                  { id: id!, payload: data },
                  { onSuccess: () => setEditOpen(false) }
                )
              }
              onCancel={() => setEditOpen(false)}
              loading={updateMutation.isPending}
            />
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default BudgetDetailPage;
