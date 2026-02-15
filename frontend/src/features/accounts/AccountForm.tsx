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
import { ACCOUNT_TYPES } from '@/types/account';
import type { Account, AccountCreate } from '@/types/account';
import { useCurrencies } from '@/hooks/useCurrencies';

const schema = z.object({
  name: z.string().min(1, 'Name is required'),
  type: z.enum(ACCOUNT_TYPES),
  currency: z.string().min(1, 'Currency is required'),
  initial_balance: z.string().regex(/^\d+(\.\d{1,6})?$/, 'Invalid amount'),
  is_active: z.boolean(),
});

type FormValues = z.infer<typeof schema>;

interface Props {
  account?: Account;
  onSubmit: (data: AccountCreate) => void;
  onCancel: () => void;
  loading?: boolean;
}

const AccountForm: React.FC<Props> = ({ account, onSubmit, onCancel, loading }) => {
  const { data: currencies = [] } = useCurrencies();
  const { control, handleSubmit, formState: { errors } } = useForm<FormValues>({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    resolver: zodResolver(schema) as any,
    defaultValues: {
      name: account?.name ?? '',
      type: account?.type ?? 'checking',
      currency: account?.currency ?? 'USD',
      initial_balance: account?.initial_balance ?? '0',
      is_active: account?.is_active ?? true,
    },
  });

  return (
    <Stack component="form" onSubmit={handleSubmit(onSubmit)} spacing={2} sx={{ pt: 1 }}>
      <Controller
        name="name"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            label="Account Name"
            error={!!errors.name}
            helperText={errors.name?.message}
            fullWidth
          />
        )}
      />
      <Controller
        name="type"
        control={control}
        render={({ field }) => (
          <TextField {...field} select label="Type" fullWidth>
            {ACCOUNT_TYPES.map((t) => (
              <MenuItem key={t} value={t}>
                {t.replace('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
              </MenuItem>
            ))}
          </TextField>
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
      {!account && (
        <Controller
          name="initial_balance"
          control={control}
          render={({ field }) => (
            <TextField
              {...field}
              label="Initial Balance"
              inputProps={{ inputMode: 'decimal' }}
              error={!!errors.initial_balance}
              helperText={errors.initial_balance?.message}
              fullWidth
            />
          )}
        />
      )}
      <Controller
        name="is_active"
        control={control}
        render={({ field }) => (
          <FormControlLabel
            control={<Switch checked={field.value} onChange={(e) => field.onChange(e.target.checked)} />}
            label="Active"
          />
        )}
      />
      <Stack direction="row" spacing={2} justifyContent="flex-end">
        <Button onClick={onCancel} disabled={loading}>Cancel</Button>
        <Button type="submit" variant="contained" disabled={loading}>
          {account ? 'Update' : 'Create'}
        </Button>
      </Stack>
    </Stack>
  );
};

export default AccountForm;
