import React, { useState } from 'react';
import { Box, Chip, IconButton, Tooltip, Typography } from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import PersonOffIcon from '@mui/icons-material/PersonOff';
import DeleteIcon from '@mui/icons-material/Delete';
import { useQuery } from '@tanstack/react-query';
import { getCurrentUser } from '@/api/users';
import { useAdminUsers, useUpdateAdminUser, useDeleteAdminUser } from './useAdminUsers';
import ConfirmDialog from '@/components/common/ConfirmDialog';
import type { User } from '@/types/user';

const AdminUsersPanel: React.FC = () => {
  const { data: users = [], isLoading } = useAdminUsers();
  const { data: currentUser } = useQuery({ queryKey: ['currentUser'], queryFn: getCurrentUser });
  const updateUser = useUpdateAdminUser();
  const deleteUser = useDeleteAdminUser();

  const [deleteTarget, setDeleteTarget] = useState<User | null>(null);

  const columns: GridColDef<User>[] = [
    { field: 'email', headerName: 'Email', flex: 2, minWidth: 180 },
    { field: 'display_name', headerName: 'Display Name', flex: 1, minWidth: 140 },
    { field: 'auth_provider', headerName: 'Provider', width: 100 },
    {
      field: 'created_at',
      headerName: 'Joined',
      width: 130,
      valueFormatter: (value: string) => new Date(value).toLocaleDateString(),
    },
    {
      field: 'is_admin',
      headerName: 'Admin',
      width: 90,
      renderCell: ({ value }) => (
        <Chip
          label={value ? 'Yes' : 'No'}
          color={value ? 'primary' : 'default'}
          size="small"
        />
      ),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 110,
      sortable: false,
      filterable: false,
      renderCell: ({ row }) => {
        const isSelf = row.id === currentUser?.id;
        return (
          <Box sx={{ display: 'flex', gap: 0.5 }}>
            <Tooltip title={row.is_admin ? 'Revoke admin' : 'Make admin'}>
              <span>
                <IconButton
                  size="small"
                  disabled={isSelf || updateUser.isPending}
                  onClick={() => updateUser.mutate({ id: row.id, payload: { is_admin: !row.is_admin } })}
                >
                  {row.is_admin ? <PersonOffIcon fontSize="small" /> : <AdminPanelSettingsIcon fontSize="small" />}
                </IconButton>
              </span>
            </Tooltip>
            <Tooltip title="Delete user">
              <span>
                <IconButton
                  size="small"
                  color="error"
                  disabled={isSelf}
                  onClick={() => setDeleteTarget(row)}
                >
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </span>
            </Tooltip>
          </Box>
        );
      },
    },
  ];

  return (
    <Box>
      <Typography variant="h6" gutterBottom>Users</Typography>
      <DataGrid
        rows={users}
        columns={columns}
        loading={isLoading}
        autoHeight
        pageSizeOptions={[25, 50, 100]}
        initialState={{ pagination: { paginationModel: { pageSize: 25 } } }}
        disableRowSelectionOnClick
      />
      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete user"
        message={`Are you sure you want to delete ${deleteTarget?.email}? This action cannot be undone.`}
        confirmLabel="Delete"
        destructive
        loading={deleteUser.isPending}
        onConfirm={() => {
          if (deleteTarget) {
            deleteUser.mutate(deleteTarget.id, { onSettled: () => setDeleteTarget(null) });
          }
        }}
        onCancel={() => setDeleteTarget(null)}
      />
    </Box>
  );
};

export default AdminUsersPanel;
