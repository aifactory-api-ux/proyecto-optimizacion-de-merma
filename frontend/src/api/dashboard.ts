import axios from 'axios';
import type { DashboardMetricsResponse } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

export const dashboardApi = {
  /**
   * Get dashboard metrics (waste, trends, alerts, demand prediction)
   * API_CONTRACT: GET /dashboard/metrics
   */
  async getMetrics(): Promise<DashboardMetricsResponse> {
    const token = localStorage.getItem('auth_token') || localStorage.getItem('access_token');
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    const response = await axios.get(`${API_BASE}/dashboard/metrics`, { headers });
    return response.data;
  },
};
