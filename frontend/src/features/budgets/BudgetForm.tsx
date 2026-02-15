import React from 'react';
import { useForm, Controller, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Box,
  Button,
  Divider,
  IconButton,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import { useCurrencies } from '@/hooks/useCurrencies';
import CategoryAutocomplete from '@/features/categories/CategoryAutocomplete';
import type { Budget, BudgetCreate } from '@/types/budget';

const schema = z.object({
  name: z.string().min(1, 'Name is required'),
  period_type: z.enum(['monthly', 'weekly', 'yearly', 'custom']),
  start_date: z.string().min(1, 'Start date required'),
  end_date: z.string().optional(),
  currency: z.string().min(1),
  budget_categories: z.array(
    z.object({
      category_id: z.string().min(1, 'Select a category'),
      limit_amount: z.string().min(1, 'Enter a limit'),
    })
  ).optional(),
});

type FormValues = z.infer<typeof schema>;

interface Props {
  budget?: Budget;
  onSubmit: (data: BudgetCreate) => void;
  onCancel: () => void;
  loading?: boolean;
}

const BudgetForm: React.FC<Props> = ({ budget, onSubmit, onCancel, loading }) => {
  const { data: currencies = [] } = useCurrencies();

  const { control, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema) as unknown as never,
    defaultValues: {
      name: budget?.name ?? '',
      period_type: budget?.period_type ?? 'monthly',
      start_date: budget?.start_date ?? new Date().toISOString().split('T')[0],
      end_date: budget?.end_date ?? '',
      currency: budget?.currency ?? 'USD',
      budget_categories: budget?.budget_categories?.map((bc) => ({
        category_id: bc.category_id,
        limit_amount: bc.limit_amount,
      })) ?? [],
    },
  });

  const { fields, append, remove } = useFieldArray({ control, name: 'budget_categories' });

  const handleFormSubmit = (values: FormValues) => {
    onSubmit({
      name: values.name,
      period_type: values.period_type,
      start_date: values.start_date,
      end_date: values.end_date || null,
      currency: values.currency,
      budget_categories: values.budget_categories?.filter(
        (bc) => bc.category_id && bc.limit_amount
      ),
    });
  };

  return (
    <Stack component="form" onSubmit={handleSubmit(handleFormSubmit)} spacing={2} sx={{ pt: 1 }}>
      <Controller
        name="name"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            label="Budget Name"
            error={!!errors.name}
            helperText={errors.name?.message}
            fullWidth
          />
        )}
      />
      <Controller
        name="period_type"
        control={control}
        render={({ field }) => (
          <TextField {...field} select label="Period Type" fullWidth>
            <MenuItem value="monthly">Monthly</MenuItem>
            <MenuItem value="weekly">Weekly</MenuItem>
            <MenuItem value="yearly">Yearly</MenuItem>
            <MenuItem value="custom">Custom</MenuItem>
          </TextField>
        )}
      />
      <Controller
        name="start_date"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            label="Start Date"
            type="date"
            InputLabelProps={{ shrink: true }}
            error={!!errors.start_date}
            helperText={errors.start_date?.message}
            fullWidth
          />
        )}
      />
      <Controller
        name="end_date"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            label="End Date (optional)"
            type="date"
            InputLabelProps={{ shrink: true }}
            fullWidth
          />
        )}
      />
      <Controller
        name="currency"
        control={control}
        render={({ field }) => (
          <TextField {...field} select label="Currency" fullWidth>
            {currencies.length > 0
              ? currencies.map((c) => (
                  <MenuItem key={c.code} value={c.code}>
                    {c.code} — {c.name}
                  </MenuItem>
                ))
              : ['USD', 'EUR', 'GBP'].map((c) => (
                  <MenuItem key={c} value={c}>{c}</MenuItem>
                ))}
          </TextField>
        )}
      />

      <Divider />

      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="subtitle2">Category Limits</Typography>
          <Button
            size="small"
            startIcon={<AddIcon />}
            onClick={() => append({ category_id: '', limit_amount: '' })}
          >
            Add
          </Button>
        </Box>
        <Stack spacing={1.5}>
          {fields.map((field, index) => (
            <Stack key={field.id} direction="row" spacing={1} alignItems="flex-start">
              <Box sx={{ flex: 1 }}>
                <Controller
                  name={`budget_categories.${index}.category_id`}
                  control={control}
                  render={({ field: f }) => (
                    <CategoryAutocomplete
                      value={f.value || null}
                      onChange={(id) => f.onChange(id ?? '')}
                      label="Category"
                      size="small"
                      error={!!errors.budget_categories?.[index]?.category_id}
                    />
                  )}
                />
              </Box>
              <Controller
                name={`budget_categories.${index}.limit_amount`}
                control={control}
                render={({ field: f }) => (
                  <TextField
                    {...f}
                    label="Limit"
                    size="small"
                    inputProps={{ inputMode: 'decimal' }}
                    sx={{ width: 120 }}
                    error={!!errors.budget_categories?.[index]?.limit_amount}
                  />
                )}
              />
              <IconButton size="small" color="error" onClick={() => remove(index)} sx={{ mt: 0.5 }}>
                <DeleteIcon fontSize="small" />
              </IconButton>
            </Stack>
          ))}
          {fields.length === 0 && (
            <Typography variant="caption" color="text.secondary">
              No limits set — add categories to track spending by category.
            </Typography>
          )}
        </Stack>
      </Box>

      <Stack direction="row" spacing={2} justifyContent="flex-end">
        <Button onClick={onCancel} disabled={loading}>Cancel</Button>
        <Button type="submit" variant="contained" disabled={loading}>
          {budget ? 'Update' : 'Create'}
        </Button>
      </Stack>
    </Stack>
  );
};

export default BudgetForm;
