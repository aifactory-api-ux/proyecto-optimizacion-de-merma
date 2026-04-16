import apiClient from './index';
import type { DashboardMetricsResponse } from '../types';

export const dashboardApi = {
  async getMetrics(): Promise<DashboardMetricsResponse> {
    const response = await apiClient.get<DashboardMetricsResponse>('/dashboard/metrics');
    return response.data;
  },
};
