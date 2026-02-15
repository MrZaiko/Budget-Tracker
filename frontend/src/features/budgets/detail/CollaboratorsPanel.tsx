import React, { useState } from 'react';
import {
  Box,
  Button,
  IconButton,
  List,
  ListItem,
  ListItemText,
  MenuItem,
  TextField,
  Typography,
  Stack,
  Chip,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import { useForm, Controller } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  useCollaborators,
  useInviteCollaborator,
  useUpdateCollaborator,
  useRemoveCollaborator,
} from '../useBudgets';
import ConfirmDialog from '@/components/common/ConfirmDialog';
import LoadingSpinner from '@/components/common/LoadingSpinner';

const schema = z.object({
  email: z.string().email('Invalid email'),
  role: z.enum(['viewer', 'editor']),
});

type FormValues = z.infer<typeof schema>;

interface Props {
  budgetId: string;
}

const CollaboratorsPanel: React.FC<Props> = ({ budgetId }) => {
  const { data: collaborators = [], isLoading } = useCollaborators(budgetId);
  const inviteMutation = useInviteCollaborator(budgetId);
  const updateMutation = useUpdateCollaborator(budgetId);
  const removeMutation = useRemoveCollaborator(budgetId);
  const [removeTarget, setRemoveTarget] = useState<string | null>(null);

  const { control, handleSubmit, reset, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema) as unknown as never,
    defaultValues: { email: '', role: 'viewer' },
  });

  const handleInvite = (data: FormValues) => {
    inviteMutation.mutate(data, { onSuccess: () => reset() });
  };

  if (isLoading) return <LoadingSpinner />;

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Collaborators
      </Typography>

      <Stack component="form" onSubmit={handleSubmit(handleInvite)} direction="row" spacing={2} sx={{ mb: 2 }}>
        <Controller
          name="email"
          control={control}
          render={({ field }) => (
            <TextField
              {...field}
              label="Email"
              size="small"
              error={!!errors.email}
              helperText={errors.email?.message}
              sx={{ flex: 1 }}
            />
          )}
        />
        <Controller
          name="role"
          control={control}
          render={({ field }) => (
            <TextField {...field} select label="Role" size="small" sx={{ width: 120 }}>
              <MenuItem value="viewer">Viewer</MenuItem>
              <MenuItem value="editor">Editor</MenuItem>
            </TextField>
          )}
        />
        <Button
          type="submit"
          variant="contained"
          startIcon={<AddIcon />}
          disabled={inviteMutation.isPending}
        >
          Invite
        </Button>
      </Stack>

      {collaborators.length === 0 ? (
        <Typography variant="body2" color="text.secondary">
          No collaborators yet.
        </Typography>
      ) : (
        <List dense>
          {collaborators.map((c) => (
            <ListItem
              key={c.id}
              secondaryAction={
                <IconButton
                  size="small"
                  color="error"
                  onClick={() => setRemoveTarget(c.user_id)}
                >
                  <DeleteIcon fontSize="small" />
                </IconButton>
              }
            >
              <ListItemText
                primary={c.user_id}
                secondary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip label={c.role} size="small" />
                    {c.accepted_at ? (
                      <Chip label="Accepted" color="success" size="small" />
                    ) : (
                      <Chip label="Pending" color="warning" size="small" />
                    )}
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
      )}

      <ConfirmDialog
        open={!!removeTarget}
        title="Remove Collaborator"
        message="Remove this collaborator from the budget?"
        confirmLabel="Remove"
        destructive
        onConfirm={() => {
          if (removeTarget) {
            removeMutation.mutate(removeTarget, {
              onSuccess: () => setRemoveTarget(null),
            });
          }
        }}
        onCancel={() => setRemoveTarget(null)}
        loading={removeMutation.isPending}
      />
    </Box>
  );
};

export default CollaboratorsPanel;
