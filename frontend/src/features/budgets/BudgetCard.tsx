import React from 'react';
import { Card, CardContent, Box, Typography, LinearProgress, Chip } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import type { Budget } from '@/types/budget';
import type { BudgetSummary } from '@/types/budget';
import AmountDisplay from '@/components/common/AmountDisplay';

const getBudgetColor = (pct: number): 'success' | 'warning' | 'error' => {
  if (pct < 0.75) return 'success';
  if (pct < 0.9) return 'warning';
  return 'error';
};

interface Props {
  budget: Budget;
  summary?: BudgetSummary;
  isOwned?: boolean;
}

const BudgetCard: React.FC<Props> = ({ budget, summary, isOwned = true }) => {
  const navigate = useNavigate();

  const totalSpent = summary ? parseFloat(summary.total_spent) : 0;
  const totalLimit = summary ? parseFloat(summary.total_limit) : 0;
  const pct = totalLimit > 0 ? totalSpent / totalLimit : 0;

  return (
    <Card
      sx={{ cursor: 'pointer', '&:hover': { borderColor: 'primary.main' } }}
      onClick={() => navigate(`/budgets/${budget.id}`)}
    >
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
          <Box>
            <Typography variant="subtitle1" fontWeight={600}>
              {budget.name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {budget.period_type} · {budget.start_date}
              {budget.end_date ? ` → ${budget.end_date}` : ''}
            </Typography>
          </Box>
          <Chip
            label={isOwned ? 'Owner' : 'Shared'}
            size="small"
            color={isOwned ? 'primary' : 'default'}
          />
        </Box>

        {summary ? (
          <Box sx={{ mt: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <AmountDisplay amount={summary.total_spent} currency={budget.currency} variant="body2" />
              <AmountDisplay amount={summary.total_limit} currency={budget.currency} variant="body2" color="text.secondary" />
            </Box>
            <LinearProgress
              variant="determinate"
              value={Math.min(pct * 100, 100)}
              color={getBudgetColor(pct)}
              sx={{ height: 8, borderRadius: 4 }}
            />
            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
              {(pct * 100).toFixed(0)}% used
            </Typography>
          </Box>
        ) : (
          <Typography variant="body2" color="text.secondary">
            {budget.currency}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

export default BudgetCard;
