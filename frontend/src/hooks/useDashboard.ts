import { useState, useEffect, useCallback } from 'react';
import { dashboardApi } from '../api/dashboard';
import type { DashboardMetricsResponse } from '../types';

interface UseDashboardReturn {
  metrics: DashboardMetricsResponse | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

/**
 * Custom hook for fetching and managing dashboard metrics.
 * 
 * Provides dashboard data including waste metrics, trends, alerts,
 * and demand predictions. Handles loading and error states automatically.
 * 
 * @returns Dashboard metrics data with loading and error states
 */
export function useDashboard(): UseDashboardReturn {
  const [metrics, setMetrics] = useState<DashboardMetricsResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await dashboardApi.getMetrics();
      setMetrics(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch dashboard metrics';
      setError(errorMessage);
      console.error('Dashboard fetch error:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMetrics();
  }, [fetchMetrics]);

  return {
    metrics,
    isLoading,
    error,
    refetch: fetchMetrics,
  };
}

export default useDashboard;
