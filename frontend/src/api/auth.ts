import apiClient from './index';
import type { UserLoginRequest, UserLoginResponse } from '../types';

export async function login(credentials: UserLoginRequest): Promise<UserLoginResponse> {
  const response = await apiClient.post<UserLoginResponse>('/auth/login', credentials);
  return response.data;
}

export default {
  login,
};
