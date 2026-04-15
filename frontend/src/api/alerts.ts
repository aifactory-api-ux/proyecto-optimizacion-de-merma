import axios from 'axios';
import type { Alert } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const alertsClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
alertsClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
alertsClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
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

/**
 * Fetch all active alerts
 * @returns Promise with array of active alerts
 */
export const fetchAlerts = async (): Promise<Alert[]> => {
  try {
    const response = await alertsClient.get<Alert[]>('/alerts');
    return response.data;
  } catch (error) {
    console.error('Error fetching alerts:', error);
    throw error;
  }
};

/**
 * Fetch alerts filtered by severity
 * @param severity - Filter by severity level
 * @returns Promise with filtered alerts
 */
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

/**
 * Fetch alerts for a specific product
 * @param productId - Product ID to filter alerts
 * @returns Promise with product-specific alerts
 */
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

/**
 * Fetch alerts for a specific store
 * @param storeId - Store ID to filter alerts
 * @returns Promise with store-specific alerts
 */
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

/**
 * Acknowledge an alert
 * @param alertId - ID of the alert to acknowledge
 * @returns Promise with updated alert
 */
export const acknowledgeAlert = async (alertId: number): Promise<Alert> => {
  try {
    const response = await alertsClient.patch<Alert>(`/alerts/${alertId}`, {
      acknowledged_at: new Date().toISOString(),
    });
    return response.data;
  } catch (error) {
    console.error('Error acknowledging alert:', error);
    throw error;
  }
};

/**
 * Resolve an alert
 * @param alertId - ID of the alert to resolve
 * @returns Promise with resolved alert
 */
export const resolveAlert = async (alertId: number): Promise<Alert> => {
  try {
    const response = await alertsClient.patch<Alert>(`/alerts/${alertId}`, {
      resolved_at: new Date().toISOString(),
      is_active: 0,
    });
    return response.data;
  } catch (error) {
    console.error('Error resolving alert:', error);
    throw error;
  }
};

/**
 * Get count of active alerts by severity
 * @returns Promise with alert counts by severity
 */
export const getAlertCounts = async (): Promise<{
  info: number;
  warning: number;
  critical: number;
  total: number;
}> => {
  try {
    const response = await alertsClient.get('/alerts/count');
    return response.data;
  } catch (error) {
    console.error('Error getting alert counts:', error);
    // Return default counts on error
    return { info: 0, warning: 0, critical: 0, total: 0 };
  }
};

// Added for useAlerts.ts compatibility
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
  getAlertCounts,
  getAlerts,
};
