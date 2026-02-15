import React from 'react';
import { Dialog, DialogTitle, DialogContent, IconButton } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import TransactionForm from './TransactionForm';
import { useCreateTransaction } from './useTransactions';

interface Props {
  open: boolean;
  onClose: () => void;
}

const TransactionModal: React.FC<Props> = ({ open, onClose }) => {
  const createMutation = useCreateTransaction();

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        New Transaction
        <IconButton onClick={onClose} size="small">
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      <DialogContent>
        <TransactionForm
          onSubmit={(data) => createMutation.mutate(data, { onSuccess: onClose })}
          onCancel={onClose}
          loading={createMutation.isPending}
        />
      </DialogContent>
    </Dialog>
  );
};

export default TransactionModal;
