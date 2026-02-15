import React from 'react';
import {
  Drawer,
  Box,
  Typography,
  IconButton,
  Divider,
  TextField,
  MenuItem,
  Button,
  Stack,
  Chip,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { useForm, Controller } from 'react-hook-form';
import { useBudgets } from '@/features/budgets/useBudgets';
import CategoryAutocomplete from '@/features/categories/CategoryAutocomplete';
import { useUpdateTransaction } from './useTransactions';
import type { Transaction, TransactionUpdate } from '@/types/transaction';

interface Props {
  transaction: Transaction | null;
  onClose: () => void;
}

interface FormValues {
  budget_id: string;
  category_id: string;
  amount: string;
  date: string;
  notes: string;
}

const typeColor: Record<string, 'success' | 'error' | 'info'> = {
  income: 'success',
  expense: 'error',
  transfer: 'info',
};

const TransactionEditDrawer: React.FC<Props> = ({ transaction, onClose }) => {
  const { data: budgets = [] } = useBudgets();
  const updateMutation = useUpdateTransaction();

  const { control, handleSubmit, reset } = useForm<FormValues>({
    values: transaction
      ? {
          budget_id: transaction.budget_id ?? '',
          category_id: transaction.category_id ?? '',
          amount: transaction.amount,
          date: transaction.date,
          notes: transaction.notes ?? '',
        }
      : { budget_id: '', category_id: '', amount: '', date: '', notes: '' },
  });

  const handleClose = () => {
    reset();
    onClose();
  };

  const onSubmit = (values: FormValues) => {
    if (!transaction) return;
    const payload: TransactionUpdate = {
      budget_id: values.budget_id || null,
      category_id: values.category_id || null,
      amount: values.amount !== transaction.amount ? values.amount : undefined,
      date: values.date !== transaction.date ? values.date : undefined,
      notes: values.notes || null,
    };
    updateMutation.mutate(
      { id: transaction.id, payload },
      { onSuccess: handleClose }
    );
  };

  return (
    <Drawer
      anchor="right"
      open={!!transaction}
      onClose={handleClose}
      PaperProps={{ sx: { width: { xs: '100%', sm: 400 }, p: 3 } }}
    >
      {transaction && (
        <Stack spacing={2.5} component="form" onSubmit={handleSubmit(onSubmit)} sx={{ height: '100%' }}>
          {/* Header */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <Box>
              <Typography variant="h6">Edit Transaction</Typography>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 0.5 }}>
                <Chip
                  label={transaction.type}
                  color={typeColor[transaction.type]}
                  size="small"
                />
                <Typography variant="body2" color="text.secondary">
                  {transaction.currency}
                </Typography>
              </Stack>
            </Box>
            <IconButton onClick={handleClose} size="small">
              <CloseIcon />
            </IconButton>
          </Box>

          <Divider />

          {/* Budget — primary field */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Budget
            </Typography>
            <Controller
              name="budget_id"
              control={control}
              render={({ field }) => (
                <TextField {...field} select fullWidth size="small">
                  <MenuItem value="">
                    <em>No budget</em>
                  </MenuItem>
                  {budgets.map((b) => (
                    <MenuItem key={b.id} value={b.id}>
                      {b.name}
                    </MenuItem>
                  ))}
                </TextField>
              )}
            />
          </Box>

          {/* Category */}
          {transaction.type !== 'transfer' && (
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Category
              </Typography>
              <Controller
                name="category_id"
                control={control}
                render={({ field }) => (
                  <CategoryAutocomplete
                    value={field.value || null}
                    onChange={(id) => field.onChange(id ?? '')}
                    transactionType={transaction.type as 'income' | 'expense'}
                    label=""
                    size="small"
                  />
                )}
              />
            </Box>
          )}

          {/* Amount */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Amount
            </Typography>
            <Controller
              name="amount"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  fullWidth
                  size="small"
                  inputProps={{ inputMode: 'decimal' }}
                  InputProps={{
                    endAdornment: (
                      <Typography variant="body2" color="text.secondary" sx={{ pl: 1 }}>
                        {transaction.currency}
                      </Typography>
                    ),
                  }}
                />
              )}
            />
          </Box>

          {/* Date */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Date
            </Typography>
            <Controller
              name="date"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  type="date"
                  fullWidth
                  size="small"
                  InputLabelProps={{ shrink: true }}
                />
              )}
            />
          </Box>

          {/* Notes */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Notes
            </Typography>
            <Controller
              name="notes"
              control={control}
              render={({ field }) => (
                <TextField {...field} multiline rows={3} fullWidth size="small" />
              )}
            />
          </Box>

          {/* Actions */}
          <Box sx={{ mt: 'auto', pt: 1 }}>
            <Stack direction="row" spacing={1} justifyContent="flex-end">
              <Button onClick={handleClose} disabled={updateMutation.isPending}>
                Cancel
              </Button>
              <Button
                type="submit"
                variant="contained"
                disabled={updateMutation.isPending}
              >
                Save
              </Button>
            </Stack>
          </Box>
        </Stack>
      )}
    </Drawer>
  );
};

export default TransactionEditDrawer;
