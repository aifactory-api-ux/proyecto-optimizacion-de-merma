import { useState, useCallback } from 'react';
import { wasteAPI } from '../api/waste';
import type { WasteByProductResponse, WasteTrendResponse, WasteQueryParams } from '../types';

export interface UseWasteReturn {
  wasteByProduct: WasteByProductResponse[];
  wasteTrends: WasteTrendResponse[];
  isLoading: boolean;
  error: string | null;
  fetchWasteByProduct: (params: { startDate: string; endDate: string }) => Promise<void>;
  fetchWasteTrends: (params: WasteQueryParams) => Promise<void>;
}

export function useWaste(): UseWasteReturn {
  const [wasteByProduct, setWasteByProduct] = useState<WasteByProductResponse[]>([]);
  const [wasteTrends, setWasteTrends] = useState<WasteTrendResponse[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchWasteByProduct = useCallback(async (params: { startDate: string; endDate: string }): Promise<void> => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await wasteAPI.getWasteByProduct(params);
      setWasteByProduct(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch waste by product data');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchWasteTrends = useCallback(async (params: WasteQueryParams): Promise<void> => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await wasteAPI.getWasteTrend(params);
      setWasteTrends(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch waste trend data');
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    wasteByProduct,
    wasteTrends,
    isLoading,
    error,
    fetchWasteByProduct,
    fetchWasteTrends,
  };
}

export default useWaste;
