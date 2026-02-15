import React, { useState } from 'react';
import { Drawer, Box, Typography, IconButton, Divider } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import AccountForm from './AccountForm';
import ConfirmDialog from '@/components/common/ConfirmDialog';
import { useCreateAccount, useUpdateAccount, useDeleteAccount } from './useAccounts';
import type { Account } from '@/types/account';

interface Props {
  open: boolean;
  onClose: () => void;
  account?: Account;
}

const AccountDrawer: React.FC<Props> = ({ open, onClose, account }) => {
  const [deleteOpen, setDeleteOpen] = useState(false);
  const createMutation = useCreateAccount();
  const updateMutation = useUpdateAccount();
  const deleteMutation = useDeleteAccount();

  const isEdit = !!account;
  const loading = createMutation.isPending || updateMutation.isPending;

  const handleSubmit = (data: Parameters<typeof createMutation.mutate>[0]) => {
    if (isEdit && account) {
      updateMutation.mutate(
        { id: account.id, payload: data },
        { onSuccess: onClose }
      );
    } else {
      createMutation.mutate(data, { onSuccess: onClose });
    }
  };

  const handleDelete = () => {
    if (account) {
      deleteMutation.mutate(account.id, { onSuccess: () => { setDeleteOpen(false); onClose(); } });
    }
  };

  return (
    <>
      <Drawer anchor="right" open={open} onClose={onClose} PaperProps={{ sx: { width: 400, p: 3 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">{isEdit ? 'Edit Account' : 'New Account'}</Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
        <Divider sx={{ mb: 2 }} />
        <AccountForm
          account={account}
          onSubmit={handleSubmit}
          onCancel={onClose}
          loading={loading}
        />
        {isEdit && (
          <Box sx={{ mt: 3 }}>
            <Divider sx={{ mb: 2 }} />
            <Typography
              variant="body2"
              color="error"
              sx={{ cursor: 'pointer' }}
              onClick={() => setDeleteOpen(true)}
            >
              Delete account
            </Typography>
          </Box>
        )}
      </Drawer>
      <ConfirmDialog
        open={deleteOpen}
        title="Delete Account"
        message="Are you sure you want to delete this account? This cannot be undone."
        confirmLabel="Delete"
        destructive
        onConfirm={handleDelete}
        onCancel={() => setDeleteOpen(false)}
        loading={deleteMutation.isPending}
      />
    </>
  );
};

export default AccountDrawer;
