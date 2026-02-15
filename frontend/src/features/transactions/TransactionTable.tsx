import React, { useState } from 'react';
import { DataGrid } from '@mui/x-data-grid';
import type { GridColDef, GridRowSelectionModel } from '@mui/x-data-grid';
import {
  Box,
  Button,
  Chip,
  IconButton,
  Typography,
  Card,
  CardContent,
  Stack,
  Pagination,
  Tooltip,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import { useBreakpoint } from '@/hooks/useBreakpoint';
import { useBulkDeleteTransactions, useDeleteTransaction } from './useTransactions';
import { useBudgets } from '@/features/budgets/useBudgets';
import { useCategories } from '@/features/categories/useCategories';
import ConfirmDialog from '@/components/common/ConfirmDialog';
import AmountDisplay from '@/components/common/AmountDisplay';
import EmptyState from '@/components/common/EmptyState';
import { useFilterStore } from '@/stores/filterStore';
import type { Transaction } from '@/types/transaction';

interface Props {
  transactions: Transaction[];
  total: number;
  page: number;
  pageSize: number;
  loading: boolean;
  onEdit: (tx: Transaction) => void;
}

const typeColor: Record<string, 'success' | 'error' | 'info'> = {
  income: 'success',
  expense: 'error',
  transfer: 'info',
};

/** Returns true when the transaction was entered in a different currency than the account. */
function isCrossCurrency(tx: Transaction): boolean {
  return !!(tx.account_currency && tx.currency !== tx.account_currency && tx.amount_account !== null);
}

// Mobile card list
const TransactionTableMobile: React.FC<Props> = ({ transactions, total, page, pageSize, loading, onEdit }) => {
  const { setTransactionFilters } = useFilterStore();

  if (!loading && transactions.length === 0) {
    return <EmptyState title="No transactions found" />;
  }

  return (
    <Box>
      <Stack spacing={1}>
        {transactions.map((tx) => (
          <Card key={tx.id} variant="outlined">
            <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    {tx.date}
                  </Typography>
                  {tx.notes && (
                    <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                      {tx.notes}
                    </Typography>
                  )}
                  <Chip label={tx.type} color={typeColor[tx.type]} size="small" sx={{ mt: 0.5 }} />
                </Box>
                <Box sx={{ textAlign: 'right' }}>
                  <AmountDisplay
                    amount={tx.amount}
                    currency={tx.currency}
                    type={tx.type === 'transfer' ? 'neutral' : tx.type as 'income' | 'expense'}
                    colorCoded
                    variant="subtitle2"
                  />
                  {isCrossCurrency(tx) && (
                    <Typography variant="caption" color="text.secondary" display="block">
                      ≈ {parseFloat(tx.amount_account!).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} {tx.account_currency}
                    </Typography>
                  )}
                  <IconButton size="small" onClick={() => onEdit(tx)} sx={{ mt: 0.5 }}>
                    <EditIcon fontSize="small" />
                  </IconButton>
                </Box>
              </Box>
            </CardContent>
          </Card>
        ))}
      </Stack>
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
        <Pagination
          count={Math.ceil(total / pageSize)}
          page={page}
          onChange={(_, p) => setTransactionFilters({ page: p })}
        />
      </Box>
    </Box>
  );
};

const TransactionTable: React.FC<Props> = ({ transactions, total, page, pageSize, loading, onEdit }) => {
  const { isMobile } = useBreakpoint();
  const { setTransactionFilters } = useFilterStore();
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [bulkDeleteOpen, setBulkDeleteOpen] = useState(false);
  const bulkDelete = useBulkDeleteTransactions();
  const singleDelete = useDeleteTransaction();
  const { data: budgets = [] } = useBudgets();
  const { data: categories = [] } = useCategories();

  const budgetMap = Object.fromEntries(budgets.map((b) => [b.id, b.name]));
  const categoryMap = Object.fromEntries(categories.map((c) => [c.id, c.name]));

  if (isMobile) {
    return <TransactionTableMobile transactions={transactions} total={total} page={page} pageSize={pageSize} loading={loading} onEdit={onEdit} />;
  }

  const columns: GridColDef[] = [
    { field: 'date', headerName: 'Date', width: 110 },
    {
      field: 'type',
      headerName: 'Type',
      width: 100,
      renderCell: (params) => (
        <Chip label={params.value} color={typeColor[params.value as string]} size="small" />
      ),
    },
    {
      field: 'amount',
      headerName: 'Amount',
      width: 160,
      renderCell: (params) => {
        const tx = params.row as Transaction;
        const cross = isCrossCurrency(tx);
        return (
          <Box>
            <AmountDisplay
              amount={tx.amount}
              currency={tx.currency}
              type={tx.type === 'transfer' ? 'neutral' : tx.type as 'income' | 'expense'}
              colorCoded
              variant="body2"
            />
            {cross && (
              <Tooltip title={`Rate: ${parseFloat(tx.account_exchange_rate!).toFixed(6)}`}>
                <Stack direction="row" alignItems="center" spacing={0.25}>
                  <SwapHorizIcon sx={{ fontSize: 12, color: 'text.disabled' }} />
                  <Typography variant="caption" color="text.secondary">
                    {parseFloat(tx.amount_account!).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} {tx.account_currency}
                  </Typography>
                </Stack>
              </Tooltip>
            )}
          </Box>
        );
      },
    },
    {
      field: 'currency',
      headerName: 'Currency',
      width: 85,
      renderCell: (params) => {
        const tx = params.row as Transaction;
        if (isCrossCurrency(tx)) {
          return (
            <Tooltip title={`Account currency: ${tx.account_currency}`}>
              <Typography variant="body2" color="warning.main">{tx.currency}</Typography>
            </Tooltip>
          );
        }
        return <Typography variant="body2">{tx.currency}</Typography>;
      },
    },
    { field: 'notes', headerName: 'Notes', flex: 1, minWidth: 150 },
    {
      field: 'budget_id',
      headerName: 'Budget',
      width: 130,
      renderCell: (params) => {
        const name = params.value ? budgetMap[params.value as string] : null;
        return <Typography variant="body2" color={name ? 'text.primary' : 'text.disabled'}>{name ?? '—'}</Typography>;
      },
    },
    {
      field: 'category_id',
      headerName: 'Category',
      width: 130,
      renderCell: (params) => {
        const name = params.value ? categoryMap[params.value as string] : null;
        return <Typography variant="body2" color={name ? 'text.primary' : 'text.disabled'}>{name ?? '—'}</Typography>;
      },
    },
    {
      field: 'actions',
      headerName: '',
      width: 90,
      sortable: false,
      renderCell: (params) => (
        <Stack direction="row" spacing={0.5}>
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              onEdit(params.row as Transaction);
            }}
          >
            <EditIcon fontSize="small" />
          </IconButton>
          <IconButton
            size="small"
            color="error"
            onClick={(e) => {
              e.stopPropagation();
              singleDelete.mutate(params.row.id);
            }}
          >
            <DeleteIcon fontSize="small" />
          </IconButton>
        </Stack>
      ),
    },
  ];

  return (
    <Box>
      {selectedIds.length > 0 && (
        <Box sx={{ mb: 1, display: 'flex', gap: 1, alignItems: 'center' }}>
          <Typography variant="body2">{selectedIds.length} selected</Typography>
          <Button
            size="small"
            color="error"
            variant="outlined"
            startIcon={<DeleteIcon />}
            onClick={() => setBulkDeleteOpen(true)}
          >
            Delete selected
          </Button>
        </Box>
      )}
      <DataGrid
        rows={transactions}
        columns={columns}
        loading={loading}
        checkboxSelection
        rowSelectionModel={selectedIds as GridRowSelectionModel}
        onRowSelectionModelChange={(ids) => setSelectedIds(ids as string[])}
        paginationMode="server"
        rowCount={total}
        paginationModel={{ page: page - 1, pageSize }}
        onPaginationModelChange={(model) =>
          setTransactionFilters({ page: model.page + 1, page_size: model.pageSize })
        }
        pageSizeOptions={[25, 50, 100]}
        autoHeight
        disableRowSelectionOnClick
        getRowHeight={() => 'auto'}
        sx={{ '& .MuiDataGrid-cell': { py: 0.75 } }}
      />
      <ConfirmDialog
        open={bulkDeleteOpen}
        title="Delete Transactions"
        message={`Delete ${selectedIds.length} transaction(s)? This cannot be undone.`}
        confirmLabel="Delete"
        destructive
        onConfirm={() =>
          bulkDelete.mutate(selectedIds, {
            onSuccess: () => {
              setBulkDeleteOpen(false);
              setSelectedIds([]);
            },
          })
        }
        onCancel={() => setBulkDeleteOpen(false)}
        loading={bulkDelete.isPending}
      />
    </Box>
  );
};

export default TransactionTable;
