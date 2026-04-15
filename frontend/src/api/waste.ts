import apiClient from './index';
import type { WasteMetric, WasteByProductResponse, WasteTrendResponse, WasteQueryParams } from '../types';

export async function getWasteByProduct(params: WasteQueryParams): Promise<WasteByProductResponse[]> {
  const response = await apiClient.get<WasteByProductResponse[]>('/waste/by-product', {
    params: { start_date: params.startDate, end_date: params.endDate, product_id: params.product_id },
  });
  return response.data;
}

export async function getWasteTrend(params: WasteQueryParams): Promise<WasteTrendResponse[]> {
  const response = await apiClient.get<WasteTrendResponse[]>('/waste/trend', {
    params: { start_date: params.startDate, end_date: params.endDate, product_id: params.product_id },
  });
  return response.data;
}

export const wasteAPI = {
  getWasteByProduct,
  getWasteTrend,
};

export type { WasteByProductResponse, WasteTrendResponse, WasteQueryParams, WasteMetric };
