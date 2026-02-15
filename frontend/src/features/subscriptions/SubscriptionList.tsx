import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  List,
  ListItem,
  ListItemText,
  Skeleton,
  Typography,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { useSubscriptions, useUpcomingSubscriptions } from './useSubscriptions';
import RecurringDrawer from '@/features/recurring/RecurringDrawer';
import EmptyState from '@/components/common/EmptyState';
import AmountDisplay from '@/components/common/AmountDisplay';
import StatusChip from '@/components/common/StatusChip';
import type { RecurringRule } from '@/types/recurring';

const MonthlyCostSummary: React.FC<{ subscriptions: RecurringRule[] }> = ({ subscriptions }) => {
  const active = subscriptions.filter((s) => s.status === 'active');

  const monthlyTotal = active.reduce((sum, s) => {
    const amount = parseFloat(s.amount);
    switch (s.frequency) {
      case 'daily': return sum + amount * 30;
      case 'weekly': return sum + amount * 4.33;
      case 'monthly': return sum + amount;
      case 'yearly': return sum + amount / 12;
      default: return sum;
    }
  }, 0);

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="subtitle2" color="text.secondary">
          Monthly Cost (active subscriptions)
        </Typography>
        <Typography variant="h4" fontWeight={700}>
          {monthlyTotal.toFixed(2)}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {active.length} active subscriptions
        </Typography>
      </CardContent>
    </Card>
  );
};

const UpcomingTimeline: React.FC = () => {
  const { data: upcoming = [], isLoading } = useUpcomingSubscriptions(30);

  if (isLoading) return <Skeleton height={120} sx={{ borderRadius: 2 }} />;

  if (upcoming.length === 0) {
    return <Typography variant="body2" color="text.secondary">No upcoming renewals in the next 30 days.</Typography>;
  }

  return (
    <List dense>
      {upcoming.map((item) => (
        <ListItem key={item.id} divider>
          <ListItemText
            primary={item.name}
            secondary={`Due in ${item.days_until} day(s) — ${item.next_occurrence}`}
          />
          <AmountDisplay amount={item.amount} currency={item.currency} variant="body2" />
        </ListItem>
      ))}
    </List>
  );
};

const SubscriptionList: React.FC = () => {
  const { data: subscriptions = [], isLoading } = useSubscriptions();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selected, setSelected] = useState<RecurringRule | undefined>();

  if (isLoading) {
    return (
      <Grid container spacing={2}>
        {[1, 2, 3].map((i) => <Grid item xs={12} sm={6} key={i}><Skeleton height={120} sx={{ borderRadius: 2 }} /></Grid>)}
      </Grid>
    );
  }

  return (
    <>
      <MonthlyCostSummary subscriptions={subscriptions} />

      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>Upcoming Renewals (30 days)</Typography>
        <UpcomingTimeline />
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">All Subscriptions</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => { setSelected(undefined); setDrawerOpen(true); }}
        >
          Add Subscription
        </Button>
      </Box>

      {subscriptions.length === 0 ? (
        <EmptyState title="No subscriptions tracked" description="Mark recurring rules as subscriptions to track them here." />
      ) : (
        <Grid container spacing={2}>
          {subscriptions.map((sub) => (
            <Grid item xs={12} sm={6} md={4} key={sub.id}>
              <Card
                sx={{ cursor: 'pointer', '&:hover': { borderColor: 'primary.main' } }}
                onClick={() => { setSelected(sub); setDrawerOpen(true); }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Box>
                      <Typography variant="subtitle1" fontWeight={600}>{sub.name}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {sub.frequency} · Next: {sub.next_occurrence}
                      </Typography>
                    </Box>
                    <AmountDisplay amount={sub.amount} currency={sub.currency} variant="subtitle2" />
                  </Box>
                  <Box sx={{ mt: 1 }}>
                    <StatusChip status={sub.status} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      <RecurringDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} rule={selected} />
    </>
  );
};

export default SubscriptionList;
