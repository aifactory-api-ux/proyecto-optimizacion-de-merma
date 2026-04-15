import apiClient from './index';
import type { WasteByProductResponse, WasteTrendResponse } from '../types';

export async function getWasteByProduct(token: string, startDate: string, endDate: string): Promise<WasteByProductResponse[]> {
  const response = await apiClient.get<WasteByProductResponse[]>('/waste/by-product', {
    params: { start_date: startDate, end_date: endDate },
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
}

export async function getWasteTrend(token: string, startDate: string, endDate: string): Promise<WasteTrendResponse[]> {
  const response = await apiClient.get<WasteTrendResponse[]>('/waste/trend', {
    params: { start_date: startDate, end_date: endDate },
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
}

export const wasteAPI = {
  getWasteByProduct,
  getWasteTrend,
};

export type { WasteByProductResponse, WasteTrendResponse };
