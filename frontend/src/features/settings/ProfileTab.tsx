import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Box, Button, TextField, Typography, MenuItem, Stack, Skeleton } from '@mui/material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getCurrentUser, updateCurrentUser } from '@/api/users';
import { useCurrencies } from '@/hooks/useCurrencies';
import { useSnackbarStore } from '@/stores/snackbarStore';

const schema = z.object({
  display_name: z.string().min(1, 'Name is required'),
  base_currency: z.string().min(1),
});

type FormValues = z.infer<typeof schema>;

const ProfileTab: React.FC = () => {
  const { data: user, isLoading } = useQuery({
    queryKey: ['currentUser'],
    queryFn: getCurrentUser,
  });
  const { data: currencies = [] } = useCurrencies();
  const qc = useQueryClient();
  const show = useSnackbarStore((s) => s.showSnackbar);

  const updateMutation = useMutation({
    mutationFn: (payload: FormValues) => updateCurrentUser(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['currentUser'] });
      show('Profile updated', 'success');
    },
    onError: () => show('Failed to update profile', 'error'),
  });

  const { control, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema) as unknown as never,
    values: {
      display_name: user?.display_name ?? '',
      base_currency: user?.base_currency ?? 'USD',
    },
  });

  if (isLoading) return <Skeleton variant="rectangular" height={200} sx={{ borderRadius: 2 }} />;

  return (
    <Box>
      <Typography variant="h6" gutterBottom>Profile</Typography>
      <Stack component="form" onSubmit={handleSubmit((data) => updateMutation.mutate(data))} spacing={2} sx={{ maxWidth: 400 }}>
        <TextField
          label="Email"
          value={user?.email ?? ''}
          disabled
          fullWidth
        />
        <Controller
          name="display_name"
          control={control}
          render={({ field }) => (
            <TextField
              {...field}
              label="Display Name"
              error={!!errors.display_name}
              helperText={errors.display_name?.message}
              fullWidth
            />
          )}
        />
        <Controller
          name="base_currency"
          control={control}
          render={({ field }) => (
            <TextField {...field} select label="Base Currency" fullWidth>
              {currencies.length > 0
                ? currencies.map((c) => (
                    <MenuItem key={c.code} value={c.code}>{c.code} — {c.name}</MenuItem>
                  ))
                : ['USD', 'EUR', 'GBP'].map((c) => (
                    <MenuItem key={c} value={c}>{c}</MenuItem>
                  ))}
            </TextField>
          )}
        />
        <Button type="submit" variant="contained" disabled={updateMutation.isPending} sx={{ alignSelf: 'flex-start' }}>
          Save Changes
        </Button>
      </Stack>
    </Box>
  );
};

export default ProfileTab;
