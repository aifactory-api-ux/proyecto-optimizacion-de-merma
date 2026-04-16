/**
 * API Client Configuration
 *
 * Centralized axios instance for making HTTP requests to the backend API.
 * Uses Vite environment variables for API URL configuration.
 */

import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';

// API base URL from environment variable - must be provided at build time
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:20001/api/v1';

/**
 * Create axios instance with default configuration
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor to add authentication token
 *
 * Extracts token from localStorage and adds it to Authorization header
 * for all authenticated requests.
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Skip adding token for auth endpoints to avoid circular dependency
    const url = config.url || '';
    if (url.includes('/auth/login')) {
      return config;
    }

    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor to handle common errors
 *
 * Handles 401 Unauthorized errors by clearing token and redirecting to login.
 * Logs other errors for debugging.
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Clear invalid token
      localStorage.removeItem('access_token');
      localStorage.removeItem('auth_user_data');
      
      // Only redirect if not already on login page
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    } else if (error.response) {
      // Log server errors for debugging
      console.error('API Error:', error.response.status, error.response.data);
    } else if (error.request) {
      // Network error
      console.error('Network Error: No response received from server');
    }
    return Promise.reject(error);
  }
);

export default apiClient;
export { apiClient as api };

/**
 * Type for API response data
 */
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

/**
 * Type for paginated API responses
 */
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

/**
 * API error response type
 */
export interface ApiError {
  detail: string;
  code?: string;
}

