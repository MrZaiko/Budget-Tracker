import React, { useState } from 'react';
import {
  Box,
  Button,
  Chip,
  Dialog,
  DialogContent,
  DialogTitle,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  TextField,
  MenuItem,
  Stack,
  Typography,
  Skeleton,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import CloseIcon from '@mui/icons-material/Close';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useCategories, useCreateCategory, useUpdateCategory, useDeleteCategory } from './useCategories';
import ConfirmDialog from '@/components/common/ConfirmDialog';
import EmptyState from '@/components/common/EmptyState';
import type { Category } from '@/types/category';

const schema = z.object({
  name: z.string().min(1, 'Name is required'),
  icon: z.string().optional(),
  color: z.string().optional(),
  transaction_type: z.enum(['income', 'expense', 'both']).default('both'),
});

type FormValues = z.infer<typeof schema>;

const CategoryForm: React.FC<{
  category?: Category;
  onSubmit: (data: FormValues) => void;
  onCancel: () => void;
  loading?: boolean;
}> = ({ category, onSubmit, onCancel, loading }) => {
  const { control, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema) as unknown as never,
    defaultValues: {
      name: category?.name ?? '',
      icon: category?.icon ?? '',
      color: category?.color ?? '',
      transaction_type: category?.transaction_type ?? 'both',
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
            label="Name"
            error={!!errors.name}
            helperText={errors.name?.message}
            fullWidth
          />
        )}
      />
      <Controller
        name="transaction_type"
        control={control}
        render={({ field }) => (
          <TextField {...field} select label="Type" fullWidth>
            <MenuItem value="both">Both</MenuItem>
            <MenuItem value="income">Income</MenuItem>
            <MenuItem value="expense">Expense</MenuItem>
          </TextField>
        )}
      />
      <Controller
        name="color"
        control={control}
        render={({ field }) => (
          <TextField {...field} label="Color (hex, optional)" placeholder="#1976d2" fullWidth />
        )}
      />
      <Controller
        name="icon"
        control={control}
        render={({ field }) => (
          <TextField {...field} label="Icon (emoji or name, optional)" fullWidth />
        )}
      />
      <Stack direction="row" spacing={2} justifyContent="flex-end">
        <Button onClick={onCancel} disabled={loading}>Cancel</Button>
        <Button type="submit" variant="contained" disabled={loading}>
          {category ? 'Update' : 'Create'}
        </Button>
      </Stack>
    </Stack>
  );
};

const CategoriesTab: React.FC = () => {
  const { data: categories = [], isLoading } = useCategories();
  const createMutation = useCreateCategory();
  const updateMutation = useUpdateCategory();
  const deleteMutation = useDeleteCategory();

  const [formOpen, setFormOpen] = useState(false);
  const [selected, setSelected] = useState<Category | undefined>();
  const [deleteTarget, setDeleteTarget] = useState<Category | undefined>();

  const userCategories = categories.filter((c) => !c.is_system);
  const systemCategories = categories.filter((c) => c.is_system);

  if (isLoading) {
    return <Skeleton variant="rectangular" height={300} sx={{ borderRadius: 2 }} />;
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Categories</Typography>
        <Button startIcon={<AddIcon />} variant="contained" onClick={() => { setSelected(undefined); setFormOpen(true); }}>
          Add Category
        </Button>
      </Box>

      {userCategories.length === 0 ? (
        <EmptyState title="No custom categories" description="Add categories to organize your transactions." />
      ) : (
        <>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Custom
          </Typography>
          <List dense>
            {userCategories.map((cat) => (
              <ListItem key={cat.id} divider>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {cat.icon && <span>{cat.icon}</span>}
                      {cat.color && (
                        <Box sx={{ width: 12, height: 12, borderRadius: '50%', bgcolor: cat.color }} />
                      )}
                      {cat.name}
                    </Box>
                  }
                  secondary={cat.transaction_type}
                />
                <ListItemSecondaryAction>
                  <IconButton
                    size="small"
                    onClick={() => { setSelected(cat); setFormOpen(true); }}
                  >
                    <EditIcon fontSize="small" />
                  </IconButton>
                  <IconButton
                    size="small"
                    color="error"
                    onClick={() => setDeleteTarget(cat)}
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </>
      )}

      {systemCategories.length > 0 && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            System (read-only)
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {systemCategories.map((cat) => (
              <Chip key={cat.id} label={cat.name} size="small" />
            ))}
          </Box>
        </Box>
      )}

      <Dialog open={formOpen} onClose={() => setFormOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          {selected ? 'Edit Category' : 'New Category'}
          <IconButton onClick={() => setFormOpen(false)} size="small">
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <CategoryForm
            category={selected}
            onSubmit={(data) => {
              if (selected) {
                updateMutation.mutate(
                  { id: selected.id, payload: data },
                  { onSuccess: () => setFormOpen(false) }
                );
              } else {
                createMutation.mutate(data, { onSuccess: () => setFormOpen(false) });
              }
            }}
            onCancel={() => setFormOpen(false)}
            loading={createMutation.isPending || updateMutation.isPending}
          />
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete Category"
        message={`Delete category "${deleteTarget?.name}"?`}
        confirmLabel="Delete"
        destructive
        onConfirm={() => {
          if (deleteTarget) {
            deleteMutation.mutate(deleteTarget.id, {
              onSuccess: () => setDeleteTarget(undefined),
              onError: () => setDeleteTarget(undefined),
            });
          }
        }}
        onCancel={() => setDeleteTarget(undefined)}
        loading={deleteMutation.isPending}
      />
    </Box>
  );
};

export default CategoriesTab;
