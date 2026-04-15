import { useState, useEffect, useCallback } from 'react';
import { Alert } from '../types';
import { getAlerts, GetAlertsParams } from '../api/alerts';

/**
 * Custom hook for managing alerts data with React Query pattern.
 * 
 * Provides alert fetching, loading states, error handling, and refetch capabilities.
 * Alerts are cached and can be refreshed on demand or automatically.
 */
export function useAlerts(params?: GetAlertsParams) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  const [isRefetching, setIsRefetching] = useState<boolean>(false);

  const fetchAlerts = useCallback(async (isRefetch: boolean = false) => {
    if (isRefetch) {
      setIsRefetching(true);
    } else {
      setIsLoading(true);
    }
    setError(null);

    try {
      const data = await getAlerts(params);
      setAlerts(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch alerts';
      setError(new Error(errorMessage));
    } finally {
      setIsLoading(false);
      setIsRefetching(false);
    }
  }, [params]);

  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  /**
   * Manually refetch alerts data.
   * Useful for refreshing after new alerts are created or acknowledged.
   */
  const refetch = useCallback(() => {
    return fetchAlerts(true);
  }, [fetchAlerts]);

  /**
   * Get alerts filtered by severity level.
   * 
   * @param severity - Severity level to filter by
   */
  const getAlertsBySeverity = useCallback(
    (severity: Alert['severity']): Alert[] => {
      return alerts.filter((alert) => alert.severity === severity);
    },
    [alerts]
  );

  /**
   * Get count of alerts by severity.
   */
  const getAlertCounts = useCallback(() => {
    return {
      critical: alerts.filter((a) => a.severity === 'critical').length,
      warning: alerts.filter((a) => a.severity === 'warning').length,
      info: alerts.filter((a) => a.severity === 'info').length,
      total: alerts.length,
    };
  }, [alerts]);

  /**
   * Check if there are any critical alerts.
   */
  const hasCriticalAlerts = useCallback((): boolean => {
    return alerts.some((alert) => alert.severity === 'critical');
  }, [alerts]);

  return {
    alerts,
    isLoading,
    error,
    isRefetching,
    refetch,
    getAlertsBySeverity,
    getAlertCounts,
    hasCriticalAlerts,
  };
}

export default useAlerts;
