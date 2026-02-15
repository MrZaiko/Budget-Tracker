import React, { useState } from 'react';
import { Box, Button, Dialog, DialogContent, DialogTitle, Grid, IconButton, Skeleton } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import CloseIcon from '@mui/icons-material/Close';
import { useBudgets, useCreateBudget } from '@/features/budgets/useBudgets';
import BudgetCard from '@/features/budgets/BudgetCard';
import BudgetForm from '@/features/budgets/BudgetForm';
import EmptyState from '@/components/common/EmptyState';
import { useQuery } from '@tanstack/react-query';
import { getCurrentUser } from '@/api/users';

const BudgetsPage: React.FC = () => {
  const { data: budgets = [], isLoading } = useBudgets();
  const createMutation = useCreateBudget();
  const [formOpen, setFormOpen] = useState(false);
  const { data: currentUser } = useQuery({ queryKey: ['currentUser'], queryFn: getCurrentUser });

  if (isLoading) {
    return (
      <Grid container spacing={2}>
        {[1, 2, 3].map((i) => (
          <Grid item xs={12} sm={6} md={4} key={i}>
            <Skeleton variant="rectangular" height={150} sx={{ borderRadius: 2 }} />
          </Grid>
        ))}
      </Grid>
    );
  }

  return (
    <>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setFormOpen(true)}>
          Create Budget
        </Button>
      </Box>

      {budgets.length === 0 ? (
        <EmptyState
          title="No budgets yet"
          description="Create a budget to track your spending."
          actionLabel="Create Budget"
          onAction={() => setFormOpen(true)}
        />
      ) : (
        <Grid container spacing={2}>
          {budgets.map((budget) => (
            <Grid item xs={12} sm={6} md={4} key={budget.id}>
              <BudgetCard
                budget={budget}
                isOwned={budget.owner_id === currentUser?.id}
              />
            </Grid>
          ))}
        </Grid>
      )}

      <Dialog open={formOpen} onClose={() => setFormOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          Create Budget
          <IconButton onClick={() => setFormOpen(false)} size="small"><CloseIcon /></IconButton>
        </DialogTitle>
        <DialogContent>
          <BudgetForm
            onSubmit={(data) => createMutation.mutate(data, { onSuccess: () => setFormOpen(false) })}
            onCancel={() => setFormOpen(false)}
            loading={createMutation.isPending}
          />
        </DialogContent>
      </Dialog>
    </>
  );
};

export default BudgetsPage;
