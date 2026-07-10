import api from './api';

export type ExecutionStatus = 'queued' | 'running' | 'completed' | 'failed';
export type ExecutionSeverity = 'Low' | 'Medium' | 'High' | 'Critical' | null;

export type Execution = {
  id: number;
  execution_name: string;
  attack_type: string;
  target_asset: string;
  status: ExecutionStatus;
  progress: number;
  started_at: string | null;
  completed_at: string | null;
  findings_count: number;
  severity: ExecutionSeverity;
  created_by: string;
};

export type CreateExecutionRequest = {
  execution_name: string;
  attack_type: string;
  target_asset: string;
};

export async function getExecutions(): Promise<Execution[]> {
  const response = await api.get<Execution[]>('/executions');
  return response.data;
}

export async function getExecution(id: number): Promise<Execution> {
  const response = await api.get<Execution>(`/executions/${id}`);
  return response.data;
}

export async function createExecution(
  payload: CreateExecutionRequest,
): Promise<Execution> {
  const response = await api.post<Execution>('/executions', payload);
  return response.data;
}

export async function deleteExecution(id: number): Promise<void> {
  await api.delete(`/executions/${id}`);
}

export async function getLatestExecutions(limit = 20): Promise<Execution[]> {
  const response = await api.get<Execution[]>(`/executions/latest?limit=${limit}`);
  return response.data;
}
