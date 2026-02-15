import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Box,
  Button,
  Card,
  CardContent,
  Stack,
  TextField,
  Typography,
  Alert,
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { localLogin } from '@/api/users';
import { useLocalAuthStore } from '@/stores/localAuthStore';
import { isLocalAuthEnabled } from '@/lib/auth';

const schema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(1, 'Password is required'),
});

type FormValues = z.infer<typeof schema>;

const LocalLoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const setToken = useLocalAuthStore((s) => s.setToken);

  const returnTo = (location.state as { returnTo?: string } | null)?.returnTo ?? '/';

  const loginMutation = useMutation({
    mutationFn: ({ email, password }: FormValues) => localLogin(email, password),
    onSuccess: (data) => {
      setToken(data.access_token);
      navigate(returnTo, { replace: true });
    },
  });

  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema) as unknown as never,
  });

  if (!isLocalAuthEnabled()) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
        <Typography>Local auth is not enabled.</Typography>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        bgcolor: 'background.default',
      }}
    >
      <Card sx={{ width: '100%', maxWidth: 400 }}>
        <CardContent sx={{ p: 4 }}>
          <Alert severity="warning" sx={{ mb: 3 }}>
            <strong>Dev / Local Auth</strong> — for development use only
          </Alert>
          <Typography variant="h5" fontWeight={700} gutterBottom>
            Sign In
          </Typography>
          <Stack
            component="form"
            onSubmit={handleSubmit((data) => loginMutation.mutate(data))}
            spacing={2}
          >
            <TextField
              {...register('email')}
              label="Email"
              type="email"
              error={!!errors.email}
              helperText={errors.email?.message}
              fullWidth
            />
            <TextField
              {...register('password')}
              label="Password"
              type="password"
              error={!!errors.password}
              helperText={errors.password?.message}
              fullWidth
            />
            {loginMutation.isError && (
              <Alert severity="error">Invalid credentials. Please try again.</Alert>
            )}
            <Button
              type="submit"
              variant="contained"
              fullWidth
              disabled={loginMutation.isPending}
            >
              Sign In
            </Button>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
};

export default LocalLoginPage;
