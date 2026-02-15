import React, { useState } from 'react';
import { Drawer, Box, Typography, IconButton, Divider, Switch, FormControlLabel } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import RecurringForm from './RecurringForm';
import ConfirmDialog from '@/components/common/ConfirmDialog';
import { useCreateRecurringRule, useUpdateRecurringRule, useDeleteRecurringRule, usePauseResumeRule } from './useRecurring';
import type { RecurringRule } from '@/types/recurring';

interface Props {
  open: boolean;
  onClose: () => void;
  rule?: RecurringRule;
}

const RecurringDrawer: React.FC<Props> = ({ open, onClose, rule }) => {
  const [deleteOpen, setDeleteOpen] = useState(false);
  const createMutation = useCreateRecurringRule();
  const updateMutation = useUpdateRecurringRule();
  const deleteMutation = useDeleteRecurringRule();
  const pauseResumeMutation = usePauseResumeRule();

  const isEdit = !!rule;
  const loading = createMutation.isPending || updateMutation.isPending;

  const handleSubmit = (data: Parameters<typeof createMutation.mutate>[0]) => {
    if (isEdit && rule) {
      updateMutation.mutate({ id: rule.id, payload: data }, { onSuccess: onClose });
    } else {
      createMutation.mutate(data, { onSuccess: onClose });
    }
  };

  const handlePauseResume = () => {
    if (rule) {
      const newStatus = rule.status === 'active' ? 'paused' : 'active';
      pauseResumeMutation.mutate({ id: rule.id, status: newStatus });
    }
  };

  return (
    <>
      <Drawer anchor="right" open={open} onClose={onClose} PaperProps={{ sx: { width: 420, p: 3 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">{isEdit ? 'Edit Rule' : 'New Recurring Rule'}</Typography>
          <IconButton onClick={onClose} size="small"><CloseIcon /></IconButton>
        </Box>
        <Divider sx={{ mb: 2 }} />

        {isEdit && rule && (
          <Box sx={{ mb: 2 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={rule.status === 'active'}
                  onChange={handlePauseResume}
                  disabled={pauseResumeMutation.isPending}
                />
              }
              label={rule.status === 'active' ? 'Active' : 'Paused'}
            />
          </Box>
        )}

        <RecurringForm rule={rule} onSubmit={handleSubmit} onCancel={onClose} loading={loading} />

        {isEdit && (
          <Box sx={{ mt: 3 }}>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="body2" color="error" sx={{ cursor: 'pointer' }} onClick={() => setDeleteOpen(true)}>
              Delete rule
            </Typography>
          </Box>
        )}
      </Drawer>

      <ConfirmDialog
        open={deleteOpen}
        title="Delete Rule"
        message="Delete this recurring rule? This cannot be undone."
        confirmLabel="Delete"
        destructive
        onConfirm={() => {
          if (rule) deleteMutation.mutate(rule.id, { onSuccess: () => { setDeleteOpen(false); onClose(); } });
        }}
        onCancel={() => setDeleteOpen(false)}
        loading={deleteMutation.isPending}
      />
    </>
  );
};

export default RecurringDrawer;
