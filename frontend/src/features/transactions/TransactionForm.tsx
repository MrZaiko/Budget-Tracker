import React, { useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { TextField, MenuItem, Button, Stack, Alert, Typography } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { useAccounts } from '@/features/accounts/useAccounts';
import { useBudgets } from '@/features/budgets/useBudgets';
import CategoryAutocomplete from '@/features/categories/CategoryAutocomplete';
import { useCurrencies } from '@/hooks/useCurrencies';
import { getLatestRates } from '@/api/currencies';
import type { TransactionCreate } from '@/types/transaction';

const schema = z.object({
  type: z.enum(['income', 'expense', 'transfer']),
  account_id: z.string().uuid(),
  budget_id: z.string().optional().or(z.literal('')),
  category_id: z.string().uuid().optional().or(z.literal('')),
  transfer_to_account_id: z.string().uuid().optional().or(z.literal('')),
  amount: z.string().regex(/^\d+(\.\d{1,6})?$/, 'Invalid amount'),
  currency: z.string().min(1),
  date: z.string().min(1, 'Date is required'),
  notes: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

interface Props {
  onSubmit: (data: TransactionCreate) => void;
  onCancel: () => void;
  loading?: boolean;
  defaultAccountId?: string;
}

/** Convert amount from currency A to currency B using the rates map (all relative to a single base). */
function crossConvert(
  amount: number,
  from: string,
  to: string,
  base: string,
  rates: Record<string, string | number>
): number | null {
  if (from === to) return amount;
  try {
    const getRate = (code: string): number | null => {
      const r = parseFloat(rates[code] as string);
      return isFinite(r) && r > 0 ? r : null;
    };
    if (from === base) {
      const r = getRate(to);
      return r !== null ? amount * r : null;
    }
    if (to === base) {
      const r = getRate(from);
      return r !== null ? amount / r : null;
    }
    const rateFrom = getRate(from);
    const rateTo = getRate(to);
    if (!rateFrom || !rateTo) return null;
    return (amount / rateFrom) * rateTo;
  } catch {
    return null;
  }
}

const TransactionForm: React.FC<Props> = ({ onSubmit, onCancel, loading, defaultAccountId }) => {
  const { data: accounts = [] } = useAccounts();
  const { data: budgets = [] } = useBudgets();
  const { data: currencies = [] } = useCurrencies();
  const { data: latestRates } = useQuery({
    queryKey: ['latestRates'],
    queryFn: getLatestRates,
    staleTime: 5 * 60 * 1000,
  });

  const { control, handleSubmit, watch, setValue, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema) as unknown as never,
    defaultValues: {
      type: 'expense',
      account_id: defaultAccountId ?? accounts[0]?.id ?? '',
      budget_id: '',
      category_id: '',
      transfer_to_account_id: '',
      amount: '',
      currency: accounts.find((a) => a.id === defaultAccountId)?.currency ?? accounts[0]?.currency ?? 'USD',
      date: new Date().toISOString().split('T')[0],
      notes: '',
    },
  });

  const transactionType = watch('type');
  const accountId = watch('account_id');
  const selectedCurrency = watch('currency');
  const amountStr = watch('amount');
  const selectedAccount = accounts.find((a) => a.id === accountId);

  // When the account changes, reset currency to match the new account
  useEffect(() => {
    if (selectedAccount) {
      setValue('currency', selectedAccount.currency);
    }
  }, [accountId]); // eslint-disable-line react-hooks/exhaustive-deps

  // Conversion preview
  const accountCurrency = selectedAccount?.currency;
  const isCrossCurrency = accountCurrency && selectedCurrency && selectedCurrency !== accountCurrency;
  let conversionHint: string | null = null;
  if (isCrossCurrency && latestRates && amountStr && /^\d+(\.\d{1,6})?$/.test(amountStr)) {
    const converted = crossConvert(
      parseFloat(amountStr),
      selectedCurrency,
      accountCurrency,
      latestRates.base,
      latestRates.rates
    );
    if (converted !== null) {
      conversionHint = `≈ ${converted.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ${accountCurrency}`;
    }
  }

  const handleFormSubmit = (values: FormValues) => {
    const payload: TransactionCreate = {
      account_id: values.account_id,
      type: values.type,
      amount: values.amount,
      currency: values.currency || selectedAccount?.currency || 'USD',
      date: values.date,
      notes: values.notes || null,
      budget_id: values.budget_id || null,
      category_id: values.category_id || null,
      transfer_to_account_id:
        values.type === 'transfer' ? values.transfer_to_account_id || null : null,
    };
    onSubmit(payload);
  };

  return (
    <Stack component="form" onSubmit={handleSubmit(handleFormSubmit)} spacing={2} sx={{ pt: 1 }}>
      <Controller
        name="type"
        control={control}
        render={({ field }) => (
          <TextField {...field} select label="Type" fullWidth>
            <MenuItem value="income">Income</MenuItem>
            <MenuItem value="expense">Expense</MenuItem>
            <MenuItem value="transfer">Transfer</MenuItem>
          </TextField>
        )}
      />
      <Controller
        name="account_id"
        control={control}
        render={({ field }) => (
          <TextField {...field} select label="Account" fullWidth error={!!errors.account_id}>
            {accounts.map((a) => (
              <MenuItem key={a.id} value={a.id}>
                {a.name} ({a.currency})
              </MenuItem>
            ))}
          </TextField>
        )}
      />
      <Controller
        name="budget_id"
        control={control}
        render={({ field }) => (
          <TextField {...field} select label="Budget (optional)" fullWidth>
            <MenuItem value="">None</MenuItem>
            {budgets.map((b) => (
              <MenuItem key={b.id} value={b.id}>{b.name}</MenuItem>
            ))}
          </TextField>
        )}
      />
      {transactionType === 'transfer' ? (
        <Controller
          name="transfer_to_account_id"
          control={control}
          render={({ field }) => (
            <TextField {...field} select label="Transfer To" fullWidth>
              {accounts.filter((a) => a.id !== accountId).map((a) => (
                <MenuItem key={a.id} value={a.id}>
                  {a.name} ({a.currency})
                </MenuItem>
              ))}
            </TextField>
          )}
        />
      ) : (
        <Controller
          name="category_id"
          control={control}
          render={({ field }) => (
            <CategoryAutocomplete
              value={field.value || null}
              onChange={(id) => field.onChange(id ?? '')}
              transactionType={transactionType}
              label="Category (optional)"
            />
          )}
        />
      )}
      <Stack direction="row" spacing={1}>
        <Controller
          name="amount"
          control={control}
          render={({ field }) => (
            <TextField
              {...field}
              label="Amount"
              inputProps={{ inputMode: 'decimal' }}
              error={!!errors.amount}
              helperText={errors.amount?.message}
              sx={{ flex: 1 }}
            />
          )}
        />
        <Controller
          name="currency"
          control={control}
          render={({ field }) => (
            <TextField {...field} select label="Currency" sx={{ width: 110 }}>
              {currencies.map((c) => (
                <MenuItem key={c.code} value={c.code}>{c.code}</MenuItem>
              ))}
            </TextField>
          )}
        />
      </Stack>
      {isCrossCurrency && (
        <Alert severity="info" sx={{ py: 0.5 }}>
          <Typography variant="body2">
            Will be converted to {accountCurrency}
            {conversionHint ? ` — ${conversionHint}` : ' (rate unknown)'}
          </Typography>
        </Alert>
      )}
      <Controller
        name="date"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            label="Date"
            type="date"
            InputLabelProps={{ shrink: true }}
            error={!!errors.date}
            helperText={errors.date?.message}
            fullWidth
          />
        )}
      />
      <Controller
        name="notes"
        control={control}
        render={({ field }) => (
          <TextField {...field} label="Notes (optional)" multiline rows={2} fullWidth />
        )}
      />
      <Stack direction="row" spacing={2} justifyContent="flex-end">
        <Button onClick={onCancel} disabled={loading}>Cancel</Button>
        <Button type="submit" variant="contained" disabled={loading}>Save</Button>
      </Stack>
    </Stack>
  );
};

export default TransactionForm;
