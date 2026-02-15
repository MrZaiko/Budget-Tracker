import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  MenuItem,
  Skeleton,
  TextField,
  Typography,
  Switch,
  FormControlLabel,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { useRecurringRules, usePauseResumeRule } from './useRecurring';
import RecurringDrawer from './RecurringDrawer';
import EmptyState from '@/components/common/EmptyState';
import AmountDisplay from '@/components/common/AmountDisplay';
import StatusChip from '@/components/common/StatusChip';
import type { RecurringRule, RecurringStatus } from '@/types/recurring';

const RecurringCard: React.FC<{ rule: RecurringRule; onClick: () => void }> = ({ rule, onClick }) => {
  const pauseResume = usePauseResumeRule();
  return (
    <Card sx={{ cursor: 'pointer', '&:hover': { borderColor: 'primary.main' } }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box onClick={onClick} sx={{ flex: 1 }}>
            <Typography variant="subtitle1" fontWeight={600}>{rule.name}</Typography>
            <Typography variant="caption" color="text.secondary">
              {rule.frequency} · Next: {rule.next_occurrence}
            </Typography>
          </Box>
          <Box sx={{ textAlign: 'right' }}>
            <AmountDisplay amount={rule.amount} currency={rule.currency} variant="subtitle2" />
            <StatusChip status={rule.status} />
          </Box>
        </Box>
        <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
          {rule.is_subscription && <Chip label="Subscription" size="small" color="info" />}
          <FormControlLabel
            control={
              <Switch
                size="small"
                checked={rule.status === 'active'}
                onChange={() =>
                  pauseResume.mutate({
                    id: rule.id,
                    status: rule.status === 'active' ? 'paused' : 'active',
                  })
                }
                disabled={pauseResume.isPending}
                onClick={(e) => e.stopPropagation()}
              />
            }
            label={rule.status === 'active' ? 'Active' : 'Paused'}
            sx={{ ml: 0 }}
          />
        </Box>
      </CardContent>
    </Card>
  );
};

const RecurringList: React.FC = () => {
  const { data: rules = [], isLoading } = useRecurringRules();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selected, setSelected] = useState<RecurringRule | undefined>();
  const [statusFilter, setStatusFilter] = useState<RecurringStatus | ''>('');

  const filtered = statusFilter ? rules.filter((r) => r.status === statusFilter) : rules;

  if (isLoading) {
    return (
      <Grid container spacing={2}>
        {[1, 2, 3].map((i) => <Grid item xs={12} sm={6} key={i}><Skeleton height={120} sx={{ borderRadius: 2 }} /></Grid>)}
      </Grid>
    );
  }

  return (
    <>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <TextField
          select
          size="small"
          label="Status"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as RecurringStatus | '')}
          sx={{ width: 160 }}
        >
          <MenuItem value="">All</MenuItem>
          <MenuItem value="active">Active</MenuItem>
          <MenuItem value="paused">Paused</MenuItem>
          <MenuItem value="cancelled">Cancelled</MenuItem>
        </TextField>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => { setSelected(undefined); setDrawerOpen(true); }}>
          Add Rule
        </Button>
      </Box>

      {filtered.length === 0 ? (
        <EmptyState title="No recurring rules" description="Set up recurring transactions to automate your finances." />
      ) : (
        <Grid container spacing={2}>
          {filtered.map((rule) => (
            <Grid item xs={12} sm={6} key={rule.id}>
              <RecurringCard rule={rule} onClick={() => { setSelected(rule); setDrawerOpen(true); }} />
            </Grid>
          ))}
        </Grid>
      )}

      <RecurringDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} rule={selected} />
    </>
  );
};

export default RecurringList;
