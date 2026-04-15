/**
 * TypeScript interfaces for the Merma Optimization application.
 * These interfaces mirror the Pydantic models from the backend.
 */

// ==================== Auth Types ====================

/**
 * Request payload for user login
 */
export interface UserLoginRequest {
  username: string;
  password: string;
}

/**
 * Response payload from successful login
 */
export interface UserLoginResponse {
  access_token: string;
  token_type: string;
}

// ==================== Dashboard Types ====================

/**
 * Waste metric for a specific product on a specific date
 */
export interface WasteMetric {
  date: string; // ISO 8601 format
  product_id: number;
  product_name: string;
  waste_quantity: number;
  waste_cost: number;
}

/**
 * Aggregated dashboard metrics response
 */
export interface DashboardMetricsResponse {
  total_waste_quantity: number;
  total_waste_cost: number;
  waste_by_product: WasteMetric[];
  waste_trend: WasteMetric[];
  alerts: string[];
  demand_prediction?: number;
}

// ==================== Alert Types ====================

/**
 * Alert severity level
 */
export type AlertSeverity = 'info' | 'warning' | 'critical';

/**
 * Alert entity
 */
export interface Alert {
  id: number;
  created_at: string; // ISO 8601 format
  message: string;
  severity: AlertSeverity;
}

// ==================== Waste Query Types ====================

/**
 * Query parameters for waste API calls
 */
export interface WasteQueryParams {
  startDate: string;
  endDate: string;
  product_id?: number;
}

/**
 * Waste aggregated by product response
 */
export interface WasteByProductResponse {
  product_id: number;
  product_name: string;
  waste_quantity: number;
  waste_cost: number;
  date: string;
}

/**
 * Waste trend data point
 */
export interface WasteTrendResponse {
  date: string;
  waste_quantity: number;
  waste_cost: number;
  product_id?: number;
  product_name?: string;
}

// ==================== Demand Prediction Types ====================

/**
 * Demand prediction response
 */
export interface DemandPredictionResponse {
  demand_prediction: number;
}

// ==================== API Error Types ====================

/**
 * Standard API error response
 */
export interface ApiError {
  detail: string;
}

/**
 * Error response with field-specific errors
 */
export interface ValidationError {
  detail: Array<{
    loc: string[];
    msg: string;
    type: string;
  }>;
}

// ==================== Generic API Response Types ====================

/**
 * Paginated response wrapper
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

/**
 * Query parameters for date range requests
 */
export interface DateRangeParams {
  start_date: string;
  end_date: string;
}

/**
 * Query parameters for product-specific requests
 */
export interface ProductDateRangeParams extends DateRangeParams {
  product_id: number;
}

// ==================== Auth Context Types ====================

/**
 * Auth context state
 */
export interface AuthState {
  isAuthenticated: boolean;
  token: string | null;
  user: UserInfo | null;
  isLoading: boolean;
}

/**
 * User information
 */
export interface UserInfo {
  id: number;
  username: string;
  email?: string;
  role?: string;
}

// ==================== Dashboard Context Types ====================

/**
 * Dashboard context state
 */
export interface DashboardState {
  metrics: DashboardMetricsResponse | null;
  isLoading: boolean;
  error: string | null;
  lastUpdated: string | null;
}

// ==================== Alert Context Types ====================

/**
 * Alert context state
 */
export interface AlertsState {
  alerts: Alert[];
  isLoading: boolean;
  error: string | null;
}

// ==================== Waste Context Types ====================

/**
 * Waste context state
 */
export interface WasteState {
  metrics: WasteMetric[];
  trend: WasteMetric[];
  isLoading: boolean;
  error: string | null;
}

// ==================== Demand Context Types ====================

/**
 * Demand context state
 */
export interface DemandState {
  prediction: number | null;
  isLoading: boolean;
  error: string | null;
}

