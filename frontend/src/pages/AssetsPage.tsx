import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  MenuItem,
  Snackbar,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { DataGrid, type GridColDef } from '@mui/x-data-grid';
import axios, { AxiosError } from 'axios';

import {
  createAsset,
  deleteAsset,
  getAssets,
  type Asset,
  type AssetCriticality,
  type AssetInput,
  type AssetStatus,
  updateAsset,
} from '../services/assets';

type Notification = {
  open: boolean;
  message: string;
  severity: 'success' | 'error';
};

type AssetFormState = AssetInput;

const defaultFormState: AssetFormState = {
  hostname: '',
  ip_address: '',
  operating_system: '',
  asset_type: '',
  owner: '',
  environment: '',
  criticality: 'medium',
  status: 'active',
};

const criticalityOptions: AssetCriticality[] = ['low', 'medium', 'high', 'critical'];
const statusOptions: AssetStatus[] = ['active', 'inactive', 'maintenance', 'retired'];

function isValidationError(error: unknown): boolean {
  if (!axios.isAxiosError(error)) {
    return false;
  }

  const axiosError = error as AxiosError<{ detail?: unknown }>;
  return axiosError.response?.status === 422 || axiosError.response?.status === 400;
}

export default function AssetsPage() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [editingAsset, setEditingAsset] = useState<Asset | null>(null);
  const [assetToDelete, setAssetToDelete] = useState<Asset | null>(null);
  const [formState, setFormState] = useState<AssetFormState>(defaultFormState);

  const [notification, setNotification] = useState<Notification>({
    open: false,
    message: '',
    severity: 'success',
  });

  const showNotification = useCallback((message: string, severity: 'success' | 'error') => {
    setNotification({ open: true, message, severity });
  }, []);

  const loadAssets = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const data = await getAssets();
      setAssets(data);
    } catch {
      setLoadError('Unable to load assets');
      showNotification('Unable to load assets', 'error');
    } finally {
      setLoading(false);
    }
  }, [showNotification]);

  useEffect(() => {
    void loadAssets();
  }, [loadAssets]);

  const resetForm = () => {
    setFormState(defaultFormState);
    setEditingAsset(null);
  };

  const openCreateDialog = () => {
    resetForm();
    setDialogOpen(true);
  };

  const openEditDialog = (asset: Asset) => {
    setEditingAsset(asset);
    setFormState({
      hostname: asset.hostname,
      ip_address: asset.ip_address,
      operating_system: asset.operating_system,
      asset_type: asset.asset_type,
      owner: asset.owner,
      environment: asset.environment,
      criticality: asset.criticality,
      status: asset.status,
    });
    setDialogOpen(true);
  };

  const closeAssetDialog = () => {
    if (saving) {
      return;
    }
    setDialogOpen(false);
    resetForm();
  };

  const closeDeleteDialog = () => {
    if (deleting) {
      return;
    }
    setDeleteDialogOpen(false);
    setAssetToDelete(null);
  };

  const onFormChange = (field: keyof AssetFormState, value: string) => {
    setFormState((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      if (editingAsset) {
        const updated = await updateAsset(editingAsset.id, formState);
        setAssets((current) => current.map((item) => (item.id === updated.id ? updated : item)));
        showNotification('Asset updated successfully', 'success');
      } else {
        const created = await createAsset(formState);
        setAssets((current) => [...current, created]);
        showNotification('Asset created successfully', 'success');
      }
      setDialogOpen(false);
      resetForm();
    } catch (error) {
      if (isValidationError(error)) {
        showNotification('Validation failed', 'error');
      } else {
        showNotification('Validation failed', 'error');
      }
    } finally {
      setSaving(false);
    }
  };

  const askDeleteAsset = (asset: Asset) => {
    setAssetToDelete(asset);
    setDeleteDialogOpen(true);
  };

  const handleDelete = async () => {
    if (!assetToDelete) {
      return;
    }

    setDeleting(true);
    try {
      await deleteAsset(assetToDelete.id);
      setAssets((current) => current.filter((asset) => asset.id !== assetToDelete.id));
      showNotification('Asset deleted successfully', 'success');
      setDeleteDialogOpen(false);
      setAssetToDelete(null);
    } catch {
      showNotification('Validation failed', 'error');
    } finally {
      setDeleting(false);
    }
  };

  const columns = useMemo<GridColDef<Asset>[]>(
    () => [
      { field: 'hostname', headerName: 'Hostname', flex: 1.2, minWidth: 160 },
      { field: 'ip_address', headerName: 'IP Address', flex: 1, minWidth: 140 },
      { field: 'operating_system', headerName: 'Operating System', flex: 1.4, minWidth: 190 },
      { field: 'asset_type', headerName: 'Asset Type', flex: 1.1, minWidth: 150 },
      { field: 'owner', headerName: 'Owner', flex: 1.1, minWidth: 150 },
      { field: 'environment', headerName: 'Environment', flex: 0.9, minWidth: 130 },
      { field: 'criticality', headerName: 'Criticality', flex: 0.8, minWidth: 120 },
      { field: 'status', headerName: 'Status', flex: 0.8, minWidth: 120 },
      {
        field: 'actions',
        headerName: 'Actions',
        sortable: false,
        filterable: false,
        width: 190,
        renderCell: (params) => (
          <Stack direction="row" spacing={1} sx={{ mt: 0.8 }}>
            <Button size="small" variant="outlined" onClick={() => openEditDialog(params.row)}>
              Edit
            </Button>
            <Button size="small" color="error" variant="outlined" onClick={() => askDeleteAsset(params.row)}>
              Delete
            </Button>
          </Stack>
        ),
      },
    ],
    [],
  );

  return (
    <Stack spacing={3}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Box>
          <Typography variant="h4">Assets</Typography>
          <Typography color="text.secondary">Asset inventory used by upcoming execution workflows.</Typography>
        </Box>
        <Button variant="contained" onClick={openCreateDialog}>
          Add Asset
        </Button>
      </Stack>

      {loadError ? <Alert severity="warning">{loadError}</Alert> : null}

      <Card>
        <CardContent>
          {loading ? (
            <Stack alignItems="center" justifyContent="center" sx={{ py: 8 }} spacing={2}>
              <CircularProgress />
              <Typography color="text.secondary">Loading assets...</Typography>
            </Stack>
          ) : assets.length === 0 ? (
            <Stack alignItems="center" justifyContent="center" sx={{ py: 8 }} spacing={1}>
              <Typography>No assets available.</Typography>
              <Typography color="text.secondary">Create your first asset.</Typography>
            </Stack>
          ) : (
            <Box sx={{ height: 560, width: '100%' }}>
              <DataGrid
                rows={assets}
                columns={columns}
                pagination
                pageSizeOptions={[5, 10, 25]}
                initialState={{
                  pagination: { paginationModel: { pageSize: 10, page: 0 } },
                  sorting: { sortModel: [{ field: 'hostname', sort: 'asc' }] },
                }}
                disableRowSelectionOnClick
              />
            </Box>
          )}
        </CardContent>
      </Card>

      <Dialog open={dialogOpen} onClose={closeAssetDialog} fullWidth maxWidth="sm">
        <DialogTitle>{editingAsset ? 'Edit Asset' : 'Add Asset'}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Hostname"
              value={formState.hostname}
              onChange={(event) => onFormChange('hostname', event.target.value)}
              required
              fullWidth
            />
            <TextField
              label="IP Address"
              value={formState.ip_address}
              onChange={(event) => onFormChange('ip_address', event.target.value)}
              required
              fullWidth
            />
            <TextField
              label="Operating System"
              value={formState.operating_system}
              onChange={(event) => onFormChange('operating_system', event.target.value)}
              required
              fullWidth
            />
            <TextField
              label="Asset Type"
              value={formState.asset_type}
              onChange={(event) => onFormChange('asset_type', event.target.value)}
              required
              fullWidth
            />
            <TextField
              label="Owner"
              value={formState.owner}
              onChange={(event) => onFormChange('owner', event.target.value)}
              required
              fullWidth
            />
            <TextField
              label="Environment"
              value={formState.environment}
              onChange={(event) => onFormChange('environment', event.target.value)}
              required
              fullWidth
            />
            <TextField
              select
              label="Criticality"
              value={formState.criticality}
              onChange={(event) => onFormChange('criticality', event.target.value)}
              required
              fullWidth
            >
              {criticalityOptions.map((criticality) => (
                <MenuItem key={criticality} value={criticality}>
                  {criticality}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="Status"
              value={formState.status}
              onChange={(event) => onFormChange('status', event.target.value)}
              required
              fullWidth
            >
              {statusOptions.map((assetStatus) => (
                <MenuItem key={assetStatus} value={assetStatus}>
                  {assetStatus}
                </MenuItem>
              ))}
            </TextField>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeAssetDialog} disabled={saving}>
            Cancel
          </Button>
          <Button onClick={handleSave} variant="contained" disabled={saving}>
            {saving ? 'Saving...' : editingAsset ? 'Update Asset' : 'Create Asset'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={deleteDialogOpen} onClose={closeDeleteDialog} fullWidth maxWidth="xs">
        <DialogTitle>Delete Asset</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete {assetToDelete?.hostname ?? 'this asset'}?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeDeleteDialog} disabled={deleting}>
            Cancel
          </Button>
          <Button color="error" variant="contained" onClick={handleDelete} disabled={deleting}>
            {deleting ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={notification.open}
        autoHideDuration={3000}
        onClose={() => setNotification((current) => ({ ...current, open: false }))}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={() => setNotification((current) => ({ ...current, open: false }))}
          severity={notification.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Stack>
  );
}
