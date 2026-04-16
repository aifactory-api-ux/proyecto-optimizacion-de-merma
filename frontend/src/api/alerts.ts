import api from './index';
import type { Alert } from '../types';

export interface AlertsResponse {
  alerts: Alert[];
}

export interface AlertCreateRequest {
  product_id?: number;
  store_id?: number;
  severity: 'info' | 'warning' | 'critical';
  alert_type: string;
  message: string;
}

export interface AlertUpdateRequest {
  acknowledged_at?: string;
  resolved_at?: string;
  is_active?: number;
}

export const fetchAlerts = async (): Promise<Alert[]> => {
  const response = await api.get<Alert[]>('/alerts');
  return response.data;
};

export const fetchAlertsBySeverity = async (
  severity: 'info' | 'warning' | 'critical'
): Promise<Alert[]> => {
  const response = await api.get<Alert[]>('/alerts', {
    params: { severity },
  });
  return response.data;
};

export const fetchAlertsByProduct = async (productId: number): Promise<Alert[]> => {
  const response = await api.get<Alert[]>('/alerts', {
    params: { product_id: productId },
  });
  return response.data;
};

export const fetchAlertsByStore = async (storeId: number): Promise<Alert[]> => {
  const response = await api.get<Alert[]>('/alerts', {
    params: { store_id: storeId },
  });
  return response.data;
};

export const acknowledgeAlert = async (alertId: number): Promise<Alert> => {
  const response = await api.patch<Alert>(`/alerts/${alertId}/acknowledge`, {});
  return response.data;
};

export const resolveAlert = async (alertId: number): Promise<Alert> => {
  const response = await api.patch<Alert>(`/alerts/${alertId}/resolve`, {});
  return response.data;
};

export interface GetAlertsParams {
  severity?: 'info' | 'warning' | 'critical';
  product_id?: number;
  store_id?: number;
}

export const getAlerts = async (params?: GetAlertsParams): Promise<Alert[]> => {
  const response = await api.get<Alert[]>('/alerts', { params });
  return response.data;
};

export default {
  fetchAlerts,
  fetchAlertsBySeverity,
  fetchAlertsByProduct,
  fetchAlertsByStore,
  acknowledgeAlert,
  resolveAlert,
  getAlerts,
};
