/**
 * Auth utilities and helper hooks.
 * El AuthProvider y AuthContext principal viven en App.tsx.
 */

export interface AuthUser {
  id: number;
  username: string;
  email?: string;
  full_name?: string;
  is_admin: boolean;
}

const TOKEN_KEY = 'access_token';
const USER_KEY  = 'auth_user_data';

export function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setAuthToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearAuthToken(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function isTokenStored(): boolean {
  return !!localStorage.getItem(TOKEN_KEY);
}
