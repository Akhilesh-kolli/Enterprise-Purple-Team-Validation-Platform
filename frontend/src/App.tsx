import { useEffect, useMemo, useState, type FormEvent } from 'react';
import axios, { AxiosError } from 'axios';
import { BrowserRouter, Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import {
  Alert,
  AppBar,
  Avatar,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CssBaseline,
  Divider,
  Drawer,
  Grid,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Stack,
  TextField,
  ThemeProvider,
  Toolbar,
  Tooltip,
  Typography,
  createTheme,
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import Inventory2OutlinedIcon from '@mui/icons-material/Inventory2Outlined';
import PlayCircleOutlineIcon from '@mui/icons-material/PlayCircleOutline';
import FactCheckOutlinedIcon from '@mui/icons-material/FactCheckOutlined';
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined';
import SettingsOutlinedIcon from '@mui/icons-material/SettingsOutlined';
import LogoutIcon from '@mui/icons-material/Logout';
import { alpha } from '@mui/material/styles';
import api, { setApiToken } from './services/api';

type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
};

type HealthResponse = {
  status: string;
  database: string;
  redis: string;
  version: string;
};

type DashboardSummary = {
  total_assets?: number;
  executed_tests?: number;
  detection_success_rate?: number;
  latest_executions?: Array<Record<string, unknown>>;
};

type Session = {
  accessToken: string;
  refreshToken: string;
  username?: string;
  role?: string;
};

type ApiState<T> = {
  data: T | null;
  loading: boolean;
  error: string | null;
};

const TOKEN_KEY = 'purple-team-session';
const drawerWidth = 280;


const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#67e8f9',
    },
    secondary: {
      main: '#f59e0b',
    },
    background: {
      default: '#08111f',
      paper: 'rgba(10, 18, 33, 0.86)',
    },
  },
  typography: {
    fontFamily: 'Inter, system-ui, sans-serif',
    h4: {
      fontWeight: 700,
    },
    h5: {
      fontWeight: 700,
    },
    h6: {
      fontWeight: 700,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 20,
          backdropFilter: 'blur(16px)',
          border: '1px solid rgba(255,255,255,0.08)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 999,
          textTransform: 'none',
          fontWeight: 700,
        },
      },
    },
  },
});

const navItems = [
  { label: 'Dashboard', path: '/dashboard', icon: <DashboardIcon /> },
  { label: 'Assets', path: '/assets', icon: <Inventory2OutlinedIcon /> },
  { label: 'Attack Execution', path: '/attack-execution', icon: <PlayCircleOutlineIcon /> },
  { label: 'Detection Results', path: '/detection-results', icon: <FactCheckOutlinedIcon /> },
  { label: 'Reports', path: '/reports', icon: <DescriptionOutlinedIcon /> },
  { label: 'Settings', path: '/settings', icon: <SettingsOutlinedIcon /> },
];

function decodeJwt(token: string): Record<string, unknown> {
  try {
    const payload = token.split('.')[1];
    const normalized = payload.replace(/-/g, '+').replace(/_/g, '/');
    const padded = normalized + '='.repeat((4 - (normalized.length % 4)) % 4);
    return JSON.parse(atob(padded));
  } catch {
    return {};
  }
}

function getStoredSession(): Session | null {
  const raw = localStorage.getItem(TOKEN_KEY);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw) as Session;
  } catch {
    return null;
  }
}

function saveSession(session: Session | null): void {
  if (!session) {
    localStorage.removeItem(TOKEN_KEY);
    return;
  }

  localStorage.setItem(TOKEN_KEY, JSON.stringify(session));
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === '') {
    return '—';
  }

  if (typeof value === 'number') {
    return Number.isInteger(value) ? value.toString() : value.toFixed(1);
  }

  if (typeof value === 'boolean') {
    return value ? 'Yes' : 'No';
  }

  return String(value);
}

function toErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ detail?: string }>;
    return axiosError.response?.data?.detail ?? axiosError.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'Unexpected error';
}

function normalizeItems(data: unknown): Array<Record<string, unknown>> {
  if (Array.isArray(data)) {
    return data.filter((item): item is Record<string, unknown> => typeof item === 'object' && item !== null);
  }

  if (data && typeof data === 'object') {
    const container = data as Record<string, unknown>;
    for (const key of ['items', 'results', 'data', 'latest_executions']) {
      const candidate = container[key];
      if (Array.isArray(candidate)) {
        return candidate.filter((item): item is Record<string, unknown> => typeof item === 'object' && item !== null);
      }
    }
  }

  return [];
}

function useApiGet<T>(path: string, enabled = true): ApiState<T> {
  const [state, setState] = useState<ApiState<T>>({ data: null, loading: enabled, error: null });

  useEffect(() => {
    if (!enabled) {
      return;
    }

    let active = true;

    setState({ data: null, loading: true, error: null });

    api
      .get<T>(path)
      .then((response) => {
        if (active) {
          setState({ data: response.data, loading: false, error: null });
        }
      })
      .catch((error) => {
        if (active) {
          setState({ data: null, loading: false, error: toErrorMessage(error) });
        }
      });

    return () => {
      active = false;
    };
  }, [enabled, path]);

  return state;
}

function getPrimaryLabel(item: Record<string, unknown>): string {
  const preferredKeys = ['name', 'title', 'asset_name', 'execution_name', 'report_name', 'id'];
  for (const key of preferredKeys) {
    if (item[key] !== undefined && item[key] !== null) {
      return formatValue(item[key]);
    }
  }

  return 'Untitled';
}

function getSecondaryLabel(item: Record<string, unknown>): string {
  const preferredKeys = ['status', 'type', 'category', 'target', 'created_at', 'executed_at'];
  const values = preferredKeys
    .map((key) => item[key])
    .filter((value) => value !== undefined && value !== null && value !== '');

  return values.map((value) => formatValue(value)).join(' • ');
}

function valueFromSummary(summary: DashboardSummary | null, key: keyof DashboardSummary): string {
  if (!summary) {
    return '—';
  }

  return formatValue(summary[key]);
}

function MetricCard({ label, value, helpText }: { label: string; value: string; helpText: string }) {
  return (
    <Card sx={{ height: '100%', background: 'linear-gradient(180deg, rgba(103,232,249,0.12), rgba(10,18,33,0.92))' }}>
      <CardContent>
        <Stack spacing={1}>
          <Typography variant="overline" color="text.secondary">
            {label}
          </Typography>
          <Typography variant="h4">{value}</Typography>
          <Typography variant="body2" color="text.secondary">
            {helpText}
          </Typography>
        </Stack>
      </CardContent>
    </Card>
  );
}

function LoginPage({ onLogin }: { onLogin: (session: Session) => void }) {
  const navigate = useNavigate();
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('AdminPassword123');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const health = useApiGet<HealthResponse>('/health');

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const response = await api.post<TokenResponse>('/auth/login', { username, password });
      const claims = decodeJwt(response.data.access_token);
      const session: Session = {
        accessToken: response.data.access_token,
        refreshToken: response.data.refresh_token,
        username: typeof claims.username === 'string' ? claims.username : username,
        role: typeof claims.role === 'string' ? claims.role : undefined,
      };

      onLogin(session);
      navigate('/dashboard', { replace: true });
    } catch (loginError) {
      setError(toErrorMessage(loginError));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'grid',
        placeItems: 'center',
        px: 2,
        background:
          'radial-gradient(circle at top left, rgba(103,232,249,0.18), transparent 28%), radial-gradient(circle at bottom right, rgba(245,158,11,0.16), transparent 32%), linear-gradient(180deg, #08111f 0%, #050a13 100%)',
      }}
    >
      <Grid container spacing={3} sx={{ maxWidth: 1120 }}>
        <Grid item xs={12} md={6}>
          <Stack spacing={3} sx={{ pr: { md: 4 } }}>
            <Chip label="Enterprise Purple Team Validation Platform" color="primary" sx={{ width: 'fit-content' }} />
            <Typography variant="h3" sx={{ fontWeight: 800, lineHeight: 1.05 }}>
              Phase 2 frontend for purple team operations.
            </Typography>
            <Typography variant="h6" color="text.secondary" sx={{ maxWidth: 560 }}>
              Authenticate against the existing backend, then move through the operational pages for assets,
              attack execution, detections, reports, and settings.
            </Typography>
            <Card sx={{ background: 'rgba(255,255,255,0.04)' }}>
              <CardContent>
                <Stack spacing={1.5}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Backend health
                  </Typography>
                  {health.loading ? (
                    <Typography variant="body1">Checking service status...</Typography>
                  ) : health.error ? (
                    <Alert severity="error">{health.error}</Alert>
                  ) : (
                    <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                      <Chip label={`Status: ${formatValue(health.data?.status)}`} color="success" />
                      <Chip label={`Database: ${formatValue(health.data?.database)}`} />
                      <Chip label={`Redis: ${formatValue(health.data?.redis)}`} />
                      <Chip label={`Version: ${formatValue(health.data?.version)}`} variant="outlined" />
                    </Stack>
                  )}
                </Stack>
              </CardContent>
            </Card>
          </Stack>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card sx={{ background: 'rgba(10,18,33,0.88)' }}>
            <CardContent sx={{ p: 4 }}>
              <Stack spacing={3} component="form" onSubmit={submit}>
                <Stack spacing={1}>
                  <Typography variant="h5">Sign in</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Use the existing JWT login endpoint.
                  </Typography>
                </Stack>

                {error ? <Alert severity="error">{error}</Alert> : null}

                <TextField
                  label="Username"
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  fullWidth
                  required
                />
                <TextField
                  label="Password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  type="password"
                  fullWidth
                  required
                />

                <Button type="submit" variant="contained" size="large" disabled={submitting}>
                  {submitting ? 'Signing in...' : 'Login'}
                </Button>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

function DashboardPage() {
  const summary = useApiGet<DashboardSummary>('/dashboard/summary');
  const executions = useApiGet<unknown>('/executions/latest');
  const health = useApiGet<HealthResponse>('/health');
  const latestExecutions = useMemo(() => normalizeItems(summary.data?.latest_executions ?? executions.data), [executions.data, summary.data]);

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4">Dashboard</Typography>
        <Typography color="text.secondary">
          Live operational overview from backend APIs.
        </Typography>
      </Box>

      {summary.error ? <Alert severity="warning">{summary.error}</Alert> : null}

      <Grid container spacing={2.5}>
        <Grid item xs={12} sm={6} lg={3}>
          <MetricCard label="Total Assets" value={valueFromSummary(summary.data, 'total_assets')} helpText="Asset inventory from backend." />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <MetricCard label="Executed Tests" value={valueFromSummary(summary.data, 'executed_tests')} helpText="Completed validation runs." />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <MetricCard
            label="Detection Success Rate"
            value={summary.data?.detection_success_rate === undefined ? '—' : `${formatValue(summary.data.detection_success_rate)}%`}
            helpText="Backend-calculated detection effectiveness."
          />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <MetricCard
            label="Backend Status"
            value={health.loading ? 'Loading' : formatValue(health.data?.status)}
            helpText="Health endpoint for runtime status."
          />
        </Grid>
      </Grid>

      <Card>
        <CardContent>
          <Stack spacing={2}>
            <Typography variant="h6">Latest Executions</Typography>
            {executions.error ? <Alert severity="warning">{executions.error}</Alert> : null}
            {latestExecutions.length === 0 ? (
              <Typography color="text.secondary">No execution records returned by the backend yet.</Typography>
            ) : (
              <Stack spacing={1.25}>
                {latestExecutions.map((item, index) => (
                  <Box
                    key={`${getPrimaryLabel(item)}-${index}`}
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      backgroundColor: alpha('#ffffff', 0.04),
                      border: '1px solid rgba(255,255,255,0.08)',
                    }}
                  >
                    <Typography fontWeight={700}>{getPrimaryLabel(item)}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {getSecondaryLabel(item)}
                    </Typography>
                  </Box>
                ))}
              </Stack>
            )}
          </Stack>
        </CardContent>
      </Card>
    </Stack>
  );
}

function CollectionPage({ title, endpoint, description }: { title: string; endpoint: string; description: string }) {
  const response = useApiGet<unknown>(endpoint);
  const items = useMemo(() => normalizeItems(response.data), [response.data]);
  const columns = useMemo(() => {
    if (items.length === 0) {
      return [] as string[];
    }

    return Object.keys(items[0]).slice(0, 6);
  }, [items]);

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4">{title}</Typography>
        <Typography color="text.secondary">{description}</Typography>
      </Box>

      {response.error ? <Alert severity="warning">{response.error}</Alert> : null}

      <Card>
        <CardContent>
          <Stack spacing={2}>
            <Typography variant="h6">Backend Records</Typography>
            {response.loading ? (
              <Typography color="text.secondary">Loading {title.toLowerCase()}...</Typography>
            ) : items.length === 0 ? (
              <Typography color="text.secondary">No records returned by the backend.</Typography>
            ) : (
              <Box sx={{ overflowX: 'auto' }}>
                <Box component="table" sx={{ width: '100%', borderCollapse: 'collapse' }}>
                  <Box component="thead">
                    <Box component="tr">
                      {columns.map((column) => (
                        <Box
                          component="th"
                          key={column}
                          sx={{ textAlign: 'left', px: 1.5, py: 1.25, borderBottom: '1px solid rgba(255,255,255,0.1)' }}
                        >
                          {column}
                        </Box>
                      ))}
                    </Box>
                  </Box>
                  <Box component="tbody">
                    {items.map((item, index) => (
                      <Box component="tr" key={`${title}-${index}`}>
                        {columns.map((column) => (
                          <Box
                            component="td"
                            key={column}
                            sx={{ px: 1.5, py: 1.2, borderBottom: '1px solid rgba(255,255,255,0.06)', verticalAlign: 'top' }}
                          >
                            {formatValue(item[column])}
                          </Box>
                        ))}
                      </Box>
                    ))}
                  </Box>
                </Box>
              </Box>
            )}
          </Stack>
        </CardContent>
      </Card>
    </Stack>
  );
}

function SettingsPage({ session }: { session: Session }) {
  const health = useApiGet<HealthResponse>('/health');
  const claims = useMemo(() => decodeJwt(session.accessToken), [session.accessToken]);

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4">Settings</Typography>
        <Typography color="text.secondary">Session and backend context.</Typography>
      </Box>

      <Grid container spacing={2.5}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Stack spacing={1.5}>
                <Typography variant="h6">Current Session</Typography>
                <Divider />
                <Typography>Username: {formatValue(session.username)}</Typography>
                <Typography>Role: {formatValue(session.role)}</Typography>
                <Typography>User ID: {formatValue(claims.sub)}</Typography>
                <Typography>Token Type: {formatValue(claims.type ?? 'access')}</Typography>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Stack spacing={1.5}>
                <Typography variant="h6">Backend Health</Typography>
                <Divider />
                {health.loading ? (
                  <Typography color="text.secondary">Loading health status...</Typography>
                ) : health.error ? (
                  <Alert severity="error">{health.error}</Alert>
                ) : (
                  <>
                    <Typography>Status: {formatValue(health.data?.status)}</Typography>
                    <Typography>Database: {formatValue(health.data?.database)}</Typography>
                    <Typography>Redis: {formatValue(health.data?.redis)}</Typography>
                    <Typography>Version: {formatValue(health.data?.version)}</Typography>
                  </>
                )}
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Stack>
  );
}

function Shell({ session, onLogout }: { session: Session; onLogout: () => void }) {
  const location = useLocation();
  const navigate = useNavigate();
  const activePath = location.pathname;

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', background: 'linear-gradient(180deg, #08111f 0%, #050a13 100%)' }}>
      <AppBar position="fixed" elevation={0} sx={{ background: 'rgba(5, 10, 19, 0.8)', backdropFilter: 'blur(12px)' }}>
        <Toolbar sx={{ gap: 2 }}>
          <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 800 }}>
            Purple Team Platform
          </Typography>
          <Chip label={session.username ?? 'Signed in'} color="primary" variant="outlined" />
          <Tooltip title="Logout">
            <IconButton color="inherit" onClick={onLogout}>
              <LogoutIcon />
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            background: 'rgba(6, 12, 24, 0.95)',
            borderRight: '1px solid rgba(255,255,255,0.08)',
          },
        }}
      >
        <Toolbar />
        <Box sx={{ px: 2, py: 3 }}>
          <Stack spacing={2}>
            <Avatar sx={{ bgcolor: 'primary.main', color: 'black', fontWeight: 800 }}>{(session.username ?? 'U').slice(0, 1).toUpperCase()}</Avatar>
            <Box>
              <Typography variant="subtitle1" fontWeight={800}>
                {session.username ?? 'User'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {session.role ?? 'authenticated'}
              </Typography>
            </Box>
          </Stack>
        </Box>
        <Divider />
        <List sx={{ px: 1 }}>
          {navItems.map((item) => (
            <ListItemButton key={item.path} selected={activePath === item.path} onClick={() => navigate(item.path)} sx={{ borderRadius: 2, mb: 0.5 }}>
              <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          ))}
        </List>
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, p: 3, pt: 12 }}>
        <Routes>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/assets" element={<CollectionPage title="Assets" endpoint="/assets" description="Inventory data from the backend asset API." />} />
          <Route path="/attack-execution" element={<CollectionPage title="Attack Execution" endpoint="/executions" description="Execution records returned by the backend." />} />
          <Route path="/detection-results" element={<CollectionPage title="Detection Results" endpoint="/detections" description="Detection validation results from the backend." />} />
          <Route path="/reports" element={<CollectionPage title="Reports" endpoint="/reports" description="Generated reports returned by the backend." />} />
          <Route path="/settings" element={<SettingsPage session={session} />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Box>
    </Box>
  );
}

function App() {
  const [session, setSession] = useState<Session | null>(() => getStoredSession());

  useEffect(() => {
    if (session?.accessToken) {
      setApiToken(session.accessToken);
      saveSession(session);
      return;
    }

    setApiToken(null);
    saveSession(null);
  }, [session]);

  const logout = () => {
    setSession(null);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage onLogin={setSession} />} />
          <Route
            path="/*"
            element={
              session ? (
                <Shell session={session} onLogout={logout} />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;