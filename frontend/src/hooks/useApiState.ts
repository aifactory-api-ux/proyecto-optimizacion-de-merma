/**
 * API State Hook Utilities
 * 
 * Shared state management utilities for API hooks.
 * Provides reusable types and helper functions for API state management.
 */

import { useState, useCallback } from 'react';

/**
 * Standard API error response structure
 */
export interface ApiError {
  detail: string;
}

/**
 * Generic API state interface for managing loading, data, and error states
 * 
 * @template T - The type of data being fetched
 */
export interface ApiState<T> {
  /** Data returned from API */
  data: T | null;
  /** Whether a request is in progress */
  isLoading: boolean;
  /** Error object if request failed */
  error: ApiError | null;
  /** Timestamp of last successful fetch */
  lastUpdated: string | null;
}

/**
 * Initial state factory for API states
 * 
 * @template T - The type of data being managed
 * @returns Initial API state with null data, no loading, no error
 */
export function createInitialApiState<T>(): ApiState<T> {
  return {
    data: null,
    isLoading: false,
    error: null,
    lastUpdated: null,
  };
}

/**
 * Custom hook for managing generic API state
 * 
 * Provides standardized state management for API calls including
 * loading states, error handling, and data storage.
 * 
 * @template T - The type of data being fetched
 * @returns State and setter functions for API data management
 */
export function useApiState<T>() {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  /**
   * Start a loading state for an API request
   */
  const startLoading = useCallback(() => {
    setIsLoading(true);
    setError(null);
  }, []);

  /**
   * Handle successful API response
   * 
   * @param newData - The data returned from the API
   */
  const handleSuccess = useCallback((newData: T) => {
    setData(newData);
    setIsLoading(false);
    setError(null);
    setLastUpdated(new Date().toISOString());
  }, []);

  /**
   * Handle failed API response
   * 
   * @param err - Error from the API call
   */
  const handleError = useCallback((err: ApiError | unknown) => {
    setIsLoading(false);
    if (err && typeof err === 'object' && 'detail' in err) {
      setError(err as ApiError);
    } else {
      setError({ detail: 'An unexpected error occurred' });
    }
  }, []);

  /**
   * Reset state to initial values
   */
  const reset = useCallback(() => {
    setData(null);
    setIsLoading(false);
    setError(null);
    setLastUpdated(null);
  }, []);

  return {
    data,
    setData,
    isLoading,
    error,
    lastUpdated,
    startLoading,
    handleSuccess,
    handleError,
    reset,
  };
}

/**
 * Hook for managing array-based API state (multiple items)
 * 
 * @template T - The type of items in the array
 * @returns State and functions for array-based API data
 */
export function useApiListState<T>() {
  const [items, setItems] = useState<T[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  /**
   * Set loading state and clear previous error
   */
  const startLoading = useCallback(() => {
    setIsLoading(true);
    setError(null);
  }, []);

  /**
   * Replace all items with new data
   * 
   * @param newItems - New array of items
   */
  const setData = useCallback((newItems: T[]) => {
    setItems(newItems);
    setLastUpdated(new Date().toISOString());
  }, []);

  /**
   * Add new items to existing list
   * 
   * @param newItems - Items to append
   */
  const appendItems = useCallback((newItems: T[]) => {
    setItems(prev => [...prev, ...newItems]);
    setLastUpdated(new Date().toISOString());
  }, []);

  /**
   * Handle successful load
   * 
   * @param data - Data from successful API call
   */
  const handleSuccess = useCallback((data: T[]) => {
    setItems(data);
    setIsLoading(false);
    setError(null);
    setLastUpdated(new Date().toISOString());
  }, []);

  /**
   * Handle error state
   * 
   * @param err - Error from API call
   */
  const handleError = useCallback((err: ApiError | unknown) => {
    setIsLoading(false);
    if (err && typeof err === 'object' && 'detail' in err) {
      setError(err as ApiError);
    } else {
      setError({ detail: 'An unexpected error occurred' });
    }
  }, []);

  /**
   * Clear all items
   */
  const clear = useCallback(() => {
    setItems([]);
    setError(null);
    setLastUpdated(null);
  }, []);

  /**
   * Reset to initial state
   */
  const reset = useCallback(() => {
    setItems([]);
    setIsLoading(false);
    setError(null);
    setLastUpdated(null);
  }, []);

  return {
    items,
    setItems: setData,
    appendItems,
    isLoading,
    setIsLoading,
    error,
    setError,
    lastUpdated,
    startLoading,
    handleSuccess,
    handleError,
    clear,
    reset,
  };
}

/**
 * Type guard to check if an error is an ApiError
 * 
 * @param error - Error object to check
 * @returns True if error is an ApiError
 */
export function isApiError(error: unknown): error is ApiError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'detail' in error &&
    typeof (error as Record<string, unknown>).detail === 'string'
  );
}

/**
 * Extract error message from unknown error type
 * 
 * @param error - Error to extract message from
 * @returns Human-readable error message
 */
export function getErrorMessage(error: unknown): string {
  if (isApiError(error)) {
    return error.detail;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unexpected error occurred';
}
