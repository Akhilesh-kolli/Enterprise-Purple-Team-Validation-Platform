import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  LinearProgress,
  MenuItem,
  Snackbar,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { DataGrid, type GridColDef } from '@mui/x-data-grid';
import axios, { AxiosError } from 'axios';

import { getAssets, type Asset } from '../services/assets';
import {
  createExecution,
  getLatestExecutions,
  type CreateExecutionRequest,
  type Execution,
  type ExecutionSeverity,
  type ExecutionStatus,
} from '../services/executions';

type Notification = {
  open: boolean;
  message: string;
  severity: 'success' | 'error';
};

const attackTypes = [
  'Reconnaissance',
  'Credential Access',
  'Privilege Escalation',
  'Persistence',
  'Defense Evasion',
  'Lateral Movement',
  'Command & Control',
  'Exfiltration',
];

const statusColorMap: Record<ExecutionStatus, 'default' | 'info' | 'success' | 'error'> = {
  queued: 'default',
  running: 'info',
  completed: 'success',
  failed: 'error',
};

const severityColorMap: Record<Exclude<ExecutionSeverity, null>, 'success' | 'warning' | 'error'> = {
  Low: 'success',
  Medium: 'warning',
  High: 'warning',
  Critical: 'error',
};

function formatDate(value: string | null): string {
  if (!value) {
    return '—';
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString();
}

function mapExecutionError(error: unknown): string {
  if (!axios.isAxiosError(error)) {
    return 'Network error';
  }

  const axiosError = error as AxiosError<{ detail?: string }>;
  const status = axiosError.response?.status;
  if (!status) {
    return 'Network error';
  }
  if (status === 401) {
    return '401 Unauthorized';
  }
  if (status === 403) {
    return '403 Forbidden';
  }
  if (status === 404) {
    return '404 Not Found';
  }
  if (status >= 500) {
    return '500 Server Error';
  }
  return axiosError.response?.data?.detail ?? 'Request failed';
}

export default function AttackExecutionPage() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [notification, setNotification] = useState<Notification>({
    open: false,
    message: '',
    severity: 'success',
  });

  const [formState, setFormState] = useState<CreateExecutionRequest>({
    execution_name: '',
    attack_type: attackTypes[0],
    target_asset: '',
  });

  const showNotification = useCallback((message: string, severity: 'success' | 'error') => {
    setNotification({ open: true, message, severity });
  }, []);

  const loadInitialData = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const [assetData, latestExecutions] = await Promise.all([
        getAssets(),
        getLatestExecutions(50),
      ]);
      setAssets(assetData);
      setExecutions(latestExecutions);
      setFormState((current) => ({
        ...current,
        target_asset: current.target_asset || assetData[0]?.hostname || '',
      }));
    } catch (error) {
      const message = mapExecutionError(error);
      setLoadError(message);
      showNotification(message, 'error');
    } finally {
      setLoading(false);
    }
  }, [showNotification]);

  useEffect(() => {
    void loadInitialData();
  }, [loadInitialData]);

  useEffect(() => {
    const intervalId = window.setInterval(() => {
      void getLatestExecutions(50)
        .then((latest) => {
          setExecutions(latest);
        })
        .catch((error) => {
          showNotification(mapExecutionError(error), 'error');
        });
    }, 2000);

    return () => {
      window.clearInterval(intervalId);
    };
  }, [showNotification]);

  const columns = useMemo<GridColDef<Execution>[]>(
    () => [
      { field: 'id', headerName: 'ID', width: 80 },
      { field: 'execution_name', headerName: 'Execution Name', flex: 1.4, minWidth: 190 },
      { field: 'attack_type', headerName: 'Attack Type', flex: 1.2, minWidth: 160 },
      { field: 'target_asset', headerName: 'Target Asset', flex: 1, minWidth: 150 },
      {
        field: 'status',
        headerName: 'Status',
        flex: 0.9,
        minWidth: 120,
        renderCell: (params) => (
          <Chip size="small" color={statusColorMap[params.row.status]} label={params.row.status} />
        ),
      },
      {
        field: 'progress',
        headerName: 'Progress',
        flex: 1.2,
        minWidth: 180,
        renderCell: (params) => (
          <Stack sx={{ width: '100%', py: 1 }} spacing={0.4}>
            <LinearProgress variant="determinate" value={params.row.progress} />
            <Typography variant="caption" color="text.secondary">
              {params.row.progress}%
            </Typography>
          </Stack>
        ),
      },
      {
        field: 'severity',
        headerName: 'Severity',
        flex: 0.9,
        minWidth: 120,
        renderCell: (params) => {
          const severity = params.row.severity;
          if (!severity) {
            return <Typography color="text.secondary">—</Typography>;
          }
          return <Chip size="small" color={severityColorMap[severity]} label={severity} />;
        },
      },
      { field: 'findings_count', headerName: 'Findings', flex: 0.8, minWidth: 100 },
      {
        field: 'started_at',
        headerName: 'Started',
        flex: 1.2,
        minWidth: 170,
        valueGetter: (value) => formatDate(value as string | null),
      },
      {
        field: 'completed_at',
        headerName: 'Completed',
        flex: 1.2,
        minWidth: 170,
        valueGetter: (value) => formatDate(value as string | null),
      },
    ],
    [],
  );

  const executeAttack = async () => {
    setExecuting(true);
    try {
      const created = await createExecution(formState);
      setExecutions((current) => [created, ...current.filter((item) => item.id !== created.id)]);
      showNotification('Execution Started', 'success');
      setFormState((current) => ({ ...current, execution_name: '' }));
    } catch (error) {
      showNotification(mapExecutionError(error), 'error');
    } finally {
      setExecuting(false);
    }
  };

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4">Attack Execution</Typography>
        <Typography color="text.secondary">
          Launch and monitor attack simulations against registered assets.
        </Typography>
      </Box>

      <Card>
        <CardContent>
          <Stack spacing={2}>
            <Typography variant="h6">New Execution</Typography>
            <TextField
              label="Execution Name"
              value={formState.execution_name}
              onChange={(event) =>
                setFormState((current) => ({ ...current, execution_name: event.target.value }))
              }
              fullWidth
              required
            />
            <TextField
              select
              label="Attack Type"
              value={formState.attack_type}
              onChange={(event) =>
                setFormState((current) => ({ ...current, attack_type: event.target.value }))
              }
              fullWidth
              required
            >
              {attackTypes.map((attackType) => (
                <MenuItem key={attackType} value={attackType}>
                  {attackType}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="Target Asset"
              value={formState.target_asset}
              onChange={(event) =>
                setFormState((current) => ({ ...current, target_asset: event.target.value }))
              }
              fullWidth
              required
            >
              {assets.map((asset) => (
                <MenuItem key={asset.id} value={asset.hostname}>
                  {asset.hostname}
                </MenuItem>
              ))}
            </TextField>
            <Box>
              <Button
                variant="contained"
                onClick={executeAttack}
                disabled={executing || !formState.execution_name || !formState.target_asset}
              >
                {executing ? 'Starting...' : 'Execute Attack'}
              </Button>
            </Box>
          </Stack>
        </CardContent>
      </Card>

      {loadError ? <Alert severity="warning">{loadError}</Alert> : null}

      <Card>
        <CardContent>
          <Stack spacing={2}>
            <Typography variant="h6">Execution History</Typography>
            {loading ? (
              <Stack alignItems="center" justifyContent="center" sx={{ py: 8 }} spacing={2}>
                <CircularProgress />
                <Typography color="text.secondary">Loading executions...</Typography>
              </Stack>
            ) : executions.length === 0 ? (
              <Typography color="text.secondary">No executions yet.</Typography>
            ) : (
              <Box sx={{ height: 580, width: '100%' }}>
                <DataGrid
                  rows={executions}
                  columns={columns}
                  pagination
                  pageSizeOptions={[5, 10, 25, 50]}
                  initialState={{
                    pagination: { paginationModel: { pageSize: 10, page: 0 } },
                    sorting: { sortModel: [{ field: 'id', sort: 'desc' }] },
                  }}
                  disableRowSelectionOnClick
                />
              </Box>
            )}
          </Stack>
        </CardContent>
      </Card>

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
