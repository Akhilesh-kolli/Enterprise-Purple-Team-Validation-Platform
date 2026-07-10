import api from './api';

export type AssetCriticality = 'low' | 'medium' | 'high' | 'critical';
export type AssetStatus = 'active' | 'inactive' | 'maintenance' | 'retired';

export type Asset = {
  id: number;
  hostname: string;
  ip_address: string;
  operating_system: string;
  asset_type: string;
  owner: string;
  environment: string;
  criticality: AssetCriticality;
  status: AssetStatus;
  created_at: string;
  updated_at: string;
};

export type AssetInput = {
  hostname: string;
  ip_address: string;
  operating_system: string;
  asset_type: string;
  owner: string;
  environment: string;
  criticality: AssetCriticality;
  status: AssetStatus;
};

export async function getAssets(): Promise<Asset[]> {
  const response = await api.get<Asset[]>('/assets');
  return response.data;
}

export async function getAsset(id: number): Promise<Asset> {
  const response = await api.get<Asset>(`/assets/${id}`);
  return response.data;
}

export async function createAsset(payload: AssetInput): Promise<Asset> {
  const response = await api.post<Asset>('/assets', payload);
  return response.data;
}

export async function updateAsset(id: number, payload: Partial<AssetInput>): Promise<Asset> {
  const response = await api.put<Asset>(`/assets/${id}`, payload);
  return response.data;
}

export async function deleteAsset(id: number): Promise<void> {
  await api.delete(`/assets/${id}`);
}
