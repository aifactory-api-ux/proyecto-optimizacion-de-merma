/**
 * Waste Data Hook
 * 
 * Custom React hook for managing waste data fetching and state.
 * Integrates with waste API endpoints for metrics, trends, and analysis.
 */

import { useState, useCallback, useMemo } from 'react';
import { wasteAPI, WasteQueryParams, WasteByProductResponse, WasteTrendResponse } from '../api/waste';
import { ApiState, ApiError } from './useApiState';

/**
 * Query parameters for waste API calls
 */
export interface UseWasteQueryParams {
  start_date?: string;
  end_date?: string;
  product_id?: number;
}

/**
 * Waste hook return values
 */
export interface UseWasteReturn {
  // State
  wasteByProduct: WasteByProductResponse[];
  wasteTrends: WasteTrendResponse[];
  isLoading: boolean;
  error: ApiError | null;
  // Query functions
  fetchWasteByProduct: (params: WasteQueryParams) => Promise<void>;
  fetchWasteTrends: (productId: number, params: UseWasteQueryParams) => Promise<void>;
  // Data helpers
  getTotalWasteQuantity: () => number;
  getTotalWasteCost: () => number;
  getTopWastedProducts: (limit?: number) => WasteByProductResponse[];
  // Filters
  setDateRange: (start: string, end: string) => void;
  clearFilters: () => void;
}

/**
 * Custom hook for waste data management
 * 
 * Provides functions to fetch waste metrics by product and trends,
 * with built-in state management and error handling.
 * 
 * @returns Waste data state and query functions
 */
export function useWaste(): UseWasteReturn {
  // State for waste by product data
  const [wasteByProduct, setWasteByProduct] = useState<WasteByProductResponse[]>([]);
  
  // State for waste trends data
  const [wasteTrends, setWasteTrends] = useState<WasteTrendResponse[]>([]);
  
  // Loading state
  const [isLoading, setIsLoading] = useState<boolean>(false);
  
  // Error state
  const [error, setError] = useState<ApiError | null>(null);
  
  /**
   * Fetch waste metrics grouped by product
   * 
   * @param params - Query parameters including date range
   */
  const fetchWasteByProduct = useCallback(async (params: WasteQueryParams): Promise<void> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await wasteAPI.getWasteByProduct(params);
      
      if (response.alerts && response.alerts.length > 0) {
        // Handle API-level alerts if needed
        console.debug('Waste by product alerts:', response.alerts);
      }
      
      setWasteByProduct([response]);
    } catch (err) {
      const apiError: ApiError = {
        message: err instanceof Error ? err.message : 'Failed to fetch waste by product data',
        code: 'WASTE_BY_PRODUCT_ERROR',
        details: err,
      };
      setError(apiError);
    } finally {
      setIsLoading(false);
    }
  }, []);
  
  /**
   * Fetch waste trend data for a specific product
   * 
   * @param productId - Product ID to fetch trends for
   * @param params - Date range parameters
   */
  const fetchWasteTrends = useCallback(
    async (productId: number, params: UseWasteQueryParams): Promise<void> => {
      setIsLoading(true);
      setError(null);
      
      try {
        const response = await wasteAPI.getWasteTrend(productId, {
          start_date: params.start_date,
          end_date: params.end_date,
        });
        
        setWasteTrends(response);
      } catch (err) {
        const apiError: ApiError = {
          message: err instanceof Error ? err.message : 'Failed to fetch waste trend data',
          code: 'WASTE_TREND_ERROR',
          details: err,
        };
        setError(apiError);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );
  
  /**
   * Calculate total waste quantity across all products
   * 
   * @returns Total quantity wasted
   */
  const getTotalWasteQuantity = useCallback((): number => {
    return wasteByProduct.reduce((total, item) => {
      return total + item.waste_quantity;
    }, 0);
  }, [wasteByProduct]);
  
  /**
   * Calculate total waste cost across all products
   * 
   * @returns Total cost of waste
   */
  const getTotalWasteCost = useCallback((): number => {
    return wasteByProduct.reduce((total, item) => {
      return total + item.waste_cost;
    }, 0);
  }, [wasteByProduct]);
  
  /**
   * Get top wasted products sorted by quantity
   * 
   * @param limit - Number of products to return (default: 10)
   * @returns Array of top wasted products
   */
  const getTopWastedProducts = useCallback(
    (limit: number = 10): WasteByProductResponse[] => {
      return [...wasteByProduct]
        .sort((a, b) => b.waste_quantity - a.waste_quantity)
        .slice(0, limit);
    },
    [wasteByProduct]
  );
  
  /**
   * Set date range filter for future queries
   * 
   * @param start - Start date ISO string
   * @param end - End date ISO string
   */
  const setDateRange = useCallback((start: string, end: string): void => {
    // This can be used to store date range in component state
    // for use in subsequent fetch calls
    console.debug(`Date range set: ${start} to ${end}`);
  }, []);
  
  /**
   * Clear all filters and reset state
   */
  const clearFilters = useCallback((): void => {
    setWasteByProduct([]);
    setWasteTrends([]);
    setError(null);
  }, []);
  
  // Return hook interface
  return {
    // State
    wasteByProduct,
    wasteTrends,
    isLoading,
    error,
    // Query functions
    fetchWasteByProduct,
    fetchWasteTrends,
    // Data helpers
    getTotalWasteQuantity,
    getTotalWasteCost,
    getTopWastedProducts,
    // Filters
    setDateRange,
    clearFilters,
  };
}

/**
 * API State interface for error handling
 * 
 * Used internally to track API call states
 */
interface ApiState<T> {
  data: T | null;
  isLoading: boolean;
  error: ApiError | null;
}

/**
 * API Error structure
 */
interface ApiError {
  message: string;
  code: string;
  details?: unknown;
}

export default useWaste;
