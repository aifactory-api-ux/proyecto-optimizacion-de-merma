import { useState, useCallback } from 'react';
import { DemandPredictionParams, DemandPredictionResponse, demandApi } from '../api/demand';

export function useDemand() {
  const [prediction, setPrediction] = useState<DemandPredictionResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchPrediction = useCallback(async (params: DemandPredictionParams) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await demandApi.getDemandPrediction(params);
      setPrediction(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch demand prediction'));
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    prediction,
    isLoading,
    error,
    fetchPrediction,
  };
}
