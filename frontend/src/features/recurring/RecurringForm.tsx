import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  TextField,
  MenuItem,
  Button,
  Stack,
  FormControlLabel,
  Switch,
} from '@mui/material';
import { useAccounts } from '@/features/accounts/useAccounts';
import { useCategories } from '@/features/categories/useCategories';
import type { RecurringRule, RecurringRuleCreate } from '@/types/recurring';

const schema = z.object({
  name: z.string().min(1, 'Name is required'),
  account_id: z.string().uuid(),
  category_id: z.string().optional().or(z.literal('')),
  type: z.enum(['income', 'expense']),
  amount: z.string().regex(/^\d+(\.\d{1,6})?$/, 'Invalid amount'),
  currency: z.string().min(1),
  frequency: z.enum(['daily', 'weekly', 'monthly', 'yearly']),
  start_date: z.string().min(1),
  end_date: z.string().optional(),
  is_subscription: z.boolean().default(false),
  notes: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

interface Props {
  rule?: RecurringRule;
  onSubmit: (data: RecurringRuleCreate) => void;
  onCancel: () => void;
  loading?: boolean;
}

const RecurringForm: React.FC<Props> = ({ rule, onSubmit, onCancel, loading }) => {
  const { data: accounts = [] } = useAccounts();
  const { data: categories = [] } = useCategories();

  const { control, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema) as unknown as never,
    defaultValues: {
      name: rule?.name ?? '',
      account_id: rule?.account_id ?? accounts[0]?.id ?? '',
      category_id: rule?.category_id ?? '',
      type: rule?.type ?? 'expense',
      amount: rule?.amount ?? '',
      currency: rule?.currency ?? 'USD',
      frequency: rule?.frequency ?? 'monthly',
      start_date: rule?.start_date ?? new Date().toISOString().split('T')[0],
      end_date: rule?.end_date ?? '',
      is_subscription: rule?.is_subscription ?? false,
      notes: rule?.notes ?? '',
    },
  });

  const handleFormSubmit = (values: FormValues) => {
    onSubmit({
      ...values,
      category_id: values.category_id || null,
      end_date: values.end_date || null,
      notes: values.notes || null,
    });
  };

  return (
    <Stack component="form" onSubmit={handleSubmit(handleFormSubmit)} spacing={2} sx={{ pt: 1 }}>
      <Controller
        name="name"
        control={control}
        render={({ field }) => (
          <TextField {...field} label="Name" error={!!errors.name} helperText={errors.name?.message} fullWidth />
        )}
      />
      <Controller
        name="type"
        control={control}
        render={({ field }) => (
          <TextField {...field} select label="Type" fullWidth>
            <MenuItem value="income">Income</MenuItem>
            <MenuItem value="expense">Expense</MenuItem>
          </TextField>
        )}
      />
      <Controller
        name="account_id"
        control={control}
        render={({ field }) => (
          <TextField {...field} select label="Account" fullWidth>
            {accounts.map((a) => <MenuItem key={a.id} value={a.id}>{a.name}</MenuItem>)}
          </TextField>
        )}
      />
      <Controller
        name="category_id"
        control={control}
        render={({ field }) => (
          <TextField {...field} select label="Category (optional)" fullWidth>
            <MenuItem value="">None</MenuItem>
            {categories.map((c) => <MenuItem key={c.id} value={c.id}>{c.name}</MenuItem>)}
          </TextField>
        )}
      />
      <Controller
        name="amount"
        control={control}
        render={({ field }) => (
          <TextField {...field} label="Amount" inputProps={{ inputMode: 'decimal' }} error={!!errors.amount} helperText={errors.amount?.message} fullWidth />
        )}
      />
      <Controller
        name="currency"
        control={control}
        render={({ field }) => <TextField {...field} label="Currency" fullWidth />}
      />
      <Controller
        name="frequency"
        control={control}
        render={({ field }) => (
          <TextField {...field} select label="Frequency" fullWidth>
            <MenuItem value="daily">Daily</MenuItem>
            <MenuItem value="weekly">Weekly</MenuItem>
            <MenuItem value="monthly">Monthly</MenuItem>
            <MenuItem value="yearly">Yearly</MenuItem>
          </TextField>
        )}
      />
      <Controller
        name="start_date"
        control={control}
        render={({ field }) => (
          <TextField {...field} label="Start Date" type="date" InputLabelProps={{ shrink: true }} fullWidth />
        )}
      />
      <Controller
        name="end_date"
        control={control}
        render={({ field }) => (
          <TextField {...field} label="End Date (optional)" type="date" InputLabelProps={{ shrink: true }} fullWidth />
        )}
      />
      <Controller
        name="is_subscription"
        control={control}
        render={({ field }) => (
          <FormControlLabel
            control={<Switch checked={field.value} onChange={(e) => field.onChange(e.target.checked)} />}
            label="Mark as subscription"
          />
        )}
      />
      <Controller
        name="notes"
        control={control}
        render={({ field }) => <TextField {...field} label="Notes (optional)" multiline rows={2} fullWidth />}
      />
      <Stack direction="row" spacing={2} justifyContent="flex-end">
        <Button onClick={onCancel} disabled={loading}>Cancel</Button>
        <Button type="submit" variant="contained" disabled={loading}>{rule ? 'Update' : 'Create'}</Button>
      </Stack>
    </Stack>
  );
};

export default RecurringForm;
