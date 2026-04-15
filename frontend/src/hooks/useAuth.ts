import { useState, useEffect, useCallback, createContext, useContext } from 'react';
import { UserLoginRequest, UserLoginResponse } from '../types';
import { login as apiLogin } from '../api/auth';

const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';

export interface AuthUser {
  id: number;
  username: string;
  email?: string;
  full_name?: string;
  is_admin: boolean;
}

interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: AuthUser | null;
  token: string | null;
}

interface AuthContextValue extends AuthState {
  login: (credentials: UserLoginRequest) => Promise<void>;
  logout: () => void;
  checkAuth: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    isLoading: true,
    user: null,
    token: null,
  });

  const checkAuth = useCallback(() => {
    const storedToken = localStorage.getItem(TOKEN_KEY);
    const storedUser = localStorage.getItem(USER_KEY);

    if (storedToken && storedUser) {
      try {
        const user = JSON.parse(storedUser) as AuthUser;
        setAuthState({
          isAuthenticated: true,
          isLoading: false,
          user,
          token: storedToken,
        });
      } catch {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
        setAuthState({
          isAuthenticated: false,
          isLoading: false,
          user: null,
          token: null,
        });
      }
    } else {
      setAuthState({
        isAuthenticated: false,
        isLoading: false,
        user: null,
        token: null,
      });
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = useCallback(async (credentials: UserLoginRequest): Promise<void> => {
    setAuthState(prev => ({ ...prev, isLoading: true }));

    try {
      const response: UserLoginResponse = await apiLogin(credentials);
      
      const user: AuthUser = {
        id: 1,
        username: credentials.username,
        email: `${credentials.username}@example.com`,
        full_name: credentials.username,
        is_admin: false,
      };

      localStorage.setItem(TOKEN_KEY, response.access_token);
      localStorage.setItem(USER_KEY, JSON.stringify(user));

      setAuthState({
        isAuthenticated: true,
        isLoading: false,
        user,
        token: response.access_token,
      });
    } catch (error) {
      setAuthState(prev => ({ ...prev, isLoading: false }));
      throw error;
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setAuthState({
      isAuthenticated: false,
      isLoading: false,
      user: null,
      token: null,
    });
  }, []);

  const value: AuthContextValue = {
    ...authState,
    login,
    logout,
    checkAuth,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}

export function useRequireAuth(): AuthContextValue {
  const auth = useAuth();
  
  if (!auth.isAuthenticated && !auth.isLoading) {
    window.location.href = '/login';
  }
  
  return auth;
}

export function useIsAuthenticated(): boolean {
  const { isAuthenticated, isLoading } = useAuth();
  return !isLoading && isAuthenticated;
}

export function useCurrentUser(): AuthUser | null {
  const { user, isLoading } = useAuth();
  return isLoading ? null : user;
}

export function useIsAdmin(): boolean {
  const { user, isLoading } = useAuth();
  return !isLoading && (user?.is_admin ?? false);
}

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
