import axios from 'axios';
import type { Alert } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api/v1';

const alertsClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

alertsClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

alertsClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

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
  try {
    const response = await alertsClient.get<Alert[]>('/alerts');
    return response.data;
  } catch (error) {
    console.error('Error fetching alerts:', error);
    throw error;
  }
};

export const fetchAlertsBySeverity = async (
  severity: 'info' | 'warning' | 'critical'
): Promise<Alert[]> => {
  try {
    const response = await alertsClient.get<Alert[]>('/alerts', {
      params: { severity },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching alerts by severity:', error);
    throw error;
  }
};

export const fetchAlertsByProduct = async (productId: number): Promise<Alert[]> => {
  try {
    const response = await alertsClient.get<Alert[]>('/alerts', {
      params: { product_id: productId },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching alerts by product:', error);
    throw error;
  }
};

export const fetchAlertsByStore = async (storeId: number): Promise<Alert[]> => {
  try {
    const response = await alertsClient.get<Alert[]>('/alerts', {
      params: { store_id: storeId },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching alerts by store:', error);
    throw error;
  }
};

export const acknowledgeAlert = async (alertId: number): Promise<Alert> => {
  try {
    const response = await alertsClient.patch<Alert>(`/alerts/${alertId}/acknowledge`, {});
    return response.data;
  } catch (error) {
    console.error('Error acknowledging alert:', error);
    throw error;
  }
};

export const resolveAlert = async (alertId: number): Promise<Alert> => {
  try {
    const response = await alertsClient.patch<Alert>(`/alerts/${alertId}/resolve`, {});
    return response.data;
  } catch (error) {
    console.error('Error resolving alert:', error);
    throw error;
  }
};

export interface GetAlertsParams {
  severity?: 'info' | 'warning' | 'critical';
  product_id?: number;
  store_id?: number;
}

export const getAlerts = async (params?: GetAlertsParams): Promise<Alert[]> => {
  try {
    const response = await alertsClient.get<Alert[]>('/alerts', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching alerts:', error);
    throw error;
  }
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
