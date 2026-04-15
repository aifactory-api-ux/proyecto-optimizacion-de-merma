import React, { useState, FormEvent } from 'react';
import { CircularProgress } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { login } from '../api/auth';
import { useAuthContext } from '../App';

export default function LoginForm() {
  const navigate = useNavigate();
  const { login: authLogin } = useAuthContext();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    console.log('LoginForm: Intentando iniciar sesión...');

    if (!username.trim() || !password.trim()) {
      setError('Por favor, ingrese usuario y contraseña');
      setLoading(false);
      return;
    }

    try {
      console.log('LoginForm: Llamando API login...');
      const response = await login({ username: username.trim(), password });
      console.log('LoginForm: Respuesta recibido:', response);
      
      console.log('LoginForm: Guardando token...');
      authLogin(response.access_token, {
        id: 0,
        username: username.trim(),
        is_admin: false,
      });
      console.log('LoginForm: Navegando a /dashboard');
      alert('DEBUG: Login exitoso, nav to /dashboard');
      console.log('LoginForm: Antes de navigate()');
      window.location.href = '/dashboard';
      console.log('LoginForm: Después de window.location');
    } catch (err) {
      console.error('LoginForm: Error:', err);
      setError(err instanceof Error ? err.message : 'Error de autenticación. Verifique sus credenciales.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        {/* Logo / Brand */}
        <div className="login-logo">
          <div className="login-logo-icon">🌿</div>
          <h1 style={{
            fontSize: 'var(--text-2xl)',
            fontWeight: 700,
            color: 'var(--clr-text-1)',
            marginBottom: '4px',
          }}>
            Merma Optimization
          </h1>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--clr-text-2)' }}>
            Inicie sesión para acceder al sistema
          </p>
        </div>

        {/* Error banner */}
        {error && (
          <div className="alert-strip alert-strip--error" style={{ marginBottom: 'var(--sp-4)' }}>
            <span>⚠</span> {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <div className="field-group">
            <label className="field-label" htmlFor="username">Usuario</label>
            <input
              id="username"
              className="field-input"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Ingrese su usuario"
              disabled={loading}
              autoComplete="username"
              autoFocus
            />
          </div>

          <div className="field-group">
            <label className="field-label" htmlFor="password">Contraseña</label>
            <input
              id="password"
              className="field-input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              disabled={loading}
              autoComplete="current-password"
            />
          </div>

          <button
            type="submit"
            className="login-submit"
            disabled={loading}
          >
            {loading
              ? <CircularProgress size={20} color="inherit" style={{ verticalAlign: 'middle' }} />
              : 'Iniciar Sesión'}
          </button>
        </form>

        <p style={{
          marginTop: 'var(--sp-5)',
          textAlign: 'center',
          fontSize: 'var(--text-xs)',
          color: 'var(--clr-text-3)',
        }}>
          Sistema de gestión de merma · v1.0
        </p>
      </div>
    </div>
  );
}
