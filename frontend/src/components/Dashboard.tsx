import React, { useState, useEffect, useCallback } from 'react';
import {
  Grid,
  LinearProgress,
  Alert as MuiAlert,
  Tooltip,
  IconButton,
} from '@mui/material';
import { Refresh } from '@mui/icons-material';
import { useDashboard } from '../hooks/useDashboard';
import { useAlerts } from '../hooks/useAlerts';
import { useWaste } from '../hooks/useWaste';
import { useDemand } from '../hooks/useDemand';
import { formatCurrency, formatQuantity } from '../utils/format';
import { Alert } from '../types';
import WasteChart from './WasteChart';
import WasteByProductTable from './WasteByProductTable';
import AlertsList from './AlertsList';
import DemandPredictionCard from './DemandPredictionCard';

interface DashboardProps {
  onLogout?: () => void;
  user?: { id: number; username: string; is_admin: boolean } | null;
}

export default function Dashboard({ onLogout, user }: DashboardProps) {
  const [selectedDateRange] = useState<{ start: Date; end: Date }>({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    end: new Date(),
  });
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const { metrics, isLoading: metricsLoading, error: metricsError, refetch: refetchMetrics } = useDashboard();
  const { alerts, isLoading: alertsLoading, error: alertsError, refetch: refetchAlerts } = useAlerts();
  const { wasteByProduct, isLoading: wasteLoading, error: wasteError, fetchWasteByProduct } = useWaste();
  const { prediction, isLoading: predictionLoading, error: predictionError, fetchPrediction } = useDemand();

  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    try {
      await Promise.all([refetchMetrics(), refetchAlerts()]);
      await fetchWasteByProduct({
        startDate: selectedDateRange.start.toISOString(),
        endDate: selectedDateRange.end.toISOString(),
      });
      if (selectedProductId) {
        await fetchPrediction({ product_id: selectedProductId, date: new Date().toISOString() });
      }
    } finally {
      setIsRefreshing(false);
    }
  }, [refetchMetrics, refetchAlerts, fetchWasteByProduct, fetchPrediction, selectedDateRange, selectedProductId]);

  useEffect(() => {
    fetchWasteByProduct({
      startDate: selectedDateRange.start.toISOString(),
      endDate: selectedDateRange.end.toISOString(),
    });
  }, [selectedDateRange, fetchWasteByProduct]);

  useEffect(() => {
    if (selectedProductId) {
      fetchPrediction({ product_id: selectedProductId, date: new Date().toISOString() });
    }
  }, [selectedProductId, fetchPrediction]);

  const criticalAlerts = alerts?.filter((a: Alert) => a.severity === 'critical') || [];

  if (metricsLoading && !metrics) {
    return (
      <div className="dashboard-layout">
        <div style={{ padding: '40px', textAlign: 'center' }}>
          <LinearProgress />
          <p style={{ marginTop: '16px', color: 'var(--clr-text-3)', fontSize: 'var(--text-sm)' }}>
            Cargando dashboard...
          </p>
        </div>
      </div>
    );
  }

  if (metricsError) {
    return (
      <div className="dashboard-layout">
        <div style={{ padding: '24px' }}>
          <MuiAlert severity="error">
            Error al cargar el dashboard: {String(metricsError)}
          </MuiAlert>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-layout">
      {/* ── Topbar ── */}
      <header className="dashboard-topbar no-print">
        <div className="topbar-brand">
          <div className="topbar-brand-dot">MO</div>
          <div>
            <div style={{ fontWeight: 700, fontSize: 'var(--text-base)', color: 'var(--clr-text-1)' }}>
              Merma Optimization
            </div>
            <div style={{ fontSize: 'var(--text-xs)', color: 'var(--clr-text-3)' }}>
              Dashboard de control
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--sp-3)' }}>
          {user && (
            <div className="user-pill">
              <div className="user-pill-avatar">
                {user.username.charAt(0).toUpperCase()}
              </div>
              {user.username}
            </div>
          )}
          <Tooltip title="Actualizar datos">
            <span>
              <button
                className="btn--icon"
                onClick={handleRefresh}
                disabled={isRefreshing}
                style={{ border: 'none' }}
              >
                <Refresh
                  fontSize="small"
                  style={{
                    animation: isRefreshing ? 'spin 0.7s linear infinite' : 'none',
                    display: 'block',
                  }}
                />
              </button>
            </span>
          </Tooltip>
          {onLogout && (
            <button className="logout-btn" onClick={onLogout}>
              Cerrar sesión
            </button>
          )}
        </div>
      </header>

      {/* ── Content ── */}
      <main className="dashboard-content">

        {/* Critical alerts banner */}
        {criticalAlerts.length > 0 && (
          <div className="alert-strip alert-strip--error animate-slideInDown">
            <span>⚠</span>
            <strong>{criticalAlerts.length} alerta{criticalAlerts.length > 1 ? 's' : ''} crítica{criticalAlerts.length > 1 ? 's' : ''}</strong>
            &mdash; requiere{criticalAlerts.length > 1 ? 'n' : ''} atención inmediata
          </div>
        )}

        {/* ── Metric cards ── */}
        <div className="grid-4" style={{ marginBottom: 'var(--sp-6)' }}>
          <div className="metric-card metric-card--purple delay-1">
            <div className="metric-label">Costo total de merma</div>
            <div className="metric-value">{formatCurrency(metrics?.total_waste_cost || 0)}</div>
            <div className="metric-footer">↓ Últimos 30 días</div>
          </div>

          <div className="metric-card metric-card--rose delay-2">
            <div className="metric-label">Cantidad total de merma</div>
            <div className="metric-value">{formatQuantity(metrics?.total_waste_quantity || 0)}</div>
            <div className="metric-footer">Unidades / kg</div>
          </div>

          <div className="metric-card metric-card--teal delay-3">
            <div className="metric-label">Alertas activas</div>
            <div className="metric-value">{alerts?.length || 0}</div>
            <div className="metric-footer">
              <span className="badge badge--error">{criticalAlerts.length} críticas</span>
            </div>
          </div>

          <div className="metric-card metric-card--emerald delay-4">
            <div className="metric-label">Predicción de demanda</div>
            <div className="metric-value">
              {metrics?.demand_prediction !== undefined
                ? formatQuantity(metrics.demand_prediction, 0)
                : '--'}
            </div>
            <div className="metric-footer">↑ Próximos 7 días</div>
          </div>
        </div>

        {/* ── Main grid ── */}
        <Grid container spacing={3}>

          {/* Waste trend chart */}
          <Grid item xs={12} lg={8}>
            <div className="panel">
              <div className="panel-header">
                <span className="panel-title">
                  <span className="panel-title-dot" />
                  Tendencia de merma
                </span>
              </div>
              <div className="panel-body" style={{ height: 350 }}>
                {metrics?.waste_trend && metrics.waste_trend.length > 0 ? (
                  <WasteChart data={metrics.waste_trend} />
                ) : (
                  <div className="empty-state">
                    <span className="empty-state-icon">📊</span>
                    <span className="empty-state-text">No hay datos de tendencia disponibles</span>
                  </div>
                )}
              </div>
            </div>
          </Grid>

          {/* Alerts list */}
          <Grid item xs={12} lg={4}>
            <div className="panel" style={{ height: '100%' }}>
              <div className="panel-header">
                <span className="panel-title">
                  <span className="panel-title-dot" style={{ background: 'var(--clr-warning)' }} />
                  Alertas
                </span>
                <span className="badge badge--neutral">{alerts?.length || 0}</span>
              </div>
              <div style={{ maxHeight: 360, overflowY: 'auto' }}>
                {alertsLoading ? (
                  <div style={{ padding: 'var(--sp-4)' }}><LinearProgress /></div>
                ) : alertsError ? (
                  <div style={{ padding: 'var(--sp-4)' }}>
                    <MuiAlert severity="error" sx={{ fontSize: '0.8rem' }}>Error al cargar alertas</MuiAlert>
                  </div>
                ) : alerts && alerts.length > 0 ? (
                  <AlertsList alerts={alerts} maxItems={10} />
                ) : (
                  <div className="empty-state">
                    <span className="empty-state-icon">✅</span>
                    <span className="empty-state-text">Sin alertas activas</span>
                  </div>
                )}
              </div>
            </div>
          </Grid>

          {/* Waste by product table */}
          <Grid item xs={12} lg={8}>
            <div className="panel">
              <div className="panel-header">
                <span className="panel-title">
                  <span className="panel-title-dot" style={{ background: 'var(--clr-success)' }} />
                  Merma por producto
                </span>
              </div>
              <div className="panel-body" style={{ maxHeight: 420, overflowY: 'auto' }}>
                {wasteLoading ? (
                  <LinearProgress />
                ) : wasteError ? (
                  <MuiAlert severity="error">Error al cargar datos de merma</MuiAlert>
                ) : (
                  <WasteByProductTable data={wasteByProduct} />
                )}
              </div>
            </div>
          </Grid>

          {/* Demand prediction */}
          <Grid item xs={12} lg={4}>
            <div className="panel" style={{ height: '100%' }}>
              <div className="panel-header">
                <span className="panel-title">
                  <span className="panel-title-dot" style={{ background: 'var(--clr-info)' }} />
                  Predicción de demanda
                </span>
              </div>
              <div className="panel-body">
                <DemandPredictionCard
                  prediction={prediction}
                  isLoading={predictionLoading}
                  error={predictionError}
                  onProductSelect={setSelectedProductId}
                  selectedProductId={selectedProductId}
                />
              </div>
            </div>
          </Grid>
        </Grid>
      </main>
    </div>
  );
}
