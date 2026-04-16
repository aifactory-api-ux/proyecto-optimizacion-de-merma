/**
 * Demand Prediction API Client
 * 
 * Provides functions to interact with the demand prediction endpoints
 * for fetching forecasted demand for products.
 */

import { api } from "./index";
import type { DemandPredictionResponse } from "../types";

/**
 * Request parameters for getting demand predictions
 */
export interface GetDemandPredictionParams {
  product_id: number;
  date: string; // ISO 8601 format
}

/**
 * Fetches demand prediction for a specific product and date.
 * 
 * @param params - Object containing product_id and date
 * @returns Promise with the demand prediction data
 * @throws Error if the API request fails
 */
export async function getDemandPrediction(
  params: GetDemandPredictionParams
): Promise<DemandPredictionResponse> {
  const { product_id, date } = params;
  
  try {
    const response = await api.get<DemandPredictionResponse>("/demand/prediction", {
      params: {
        product_id,
        date,
      },
    });
    
    return response.data;
  } catch (error) {
    // Re-throw the error with context for the caller
    const message = error instanceof Error ? error.message : "Failed to fetch demand prediction";
    throw new Error(message);
  }
}

/**
 * Batch request parameters for multiple demand predictions
 */
export interface GetBatchDemandPredictionsParams {
  product_ids: number[];
  startDate: string; // ISO 8601 format
  endDate?: string; // ISO 8601 format
}

/**
 * Fetches demand predictions for multiple products.
 * Makes parallel requests for each product.
 *
 * @param params - Object containing product_ids and date range
 * @returns Promise with array of demand predictions
 */
export async function getBatchDemandPredictions(
  params: GetBatchDemandPredictionsParams
): Promise<DemandPredictionResponse[]> {
  const { product_ids, startDate } = params;

  const results = await Promise.all(
    product_ids.map(async (product_id) => {
      try {
        return await getDemandPrediction({
          product_id,
          date: startDate,
        });
      } catch (error) {
        console.error(`Failed to get prediction for product ${product_id}:`, error);
        return null;
      }
    })
  );

  return results.filter((p): p is DemandPredictionResponse => p !== null);
}

/**
 * Request parameters for getting predictions for a date range
 */
export interface GetDemandPredictionsRangeParams {
  product_id: number;
  startDate: string; // ISO 8601 format
  endDate: string; // ISO 8601 format
}

export const demandApi = {
  getDemandPrediction,
  getBatchDemandPredictions,
};

export type DemandPredictionParams = GetDemandPredictionParams;
export type DemandPredictionResponseType = DemandPredictionResponse;

export default demandApi;
