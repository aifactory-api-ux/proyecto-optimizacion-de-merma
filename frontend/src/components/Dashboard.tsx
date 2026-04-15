import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Chip,
  Alert as MuiAlert,
  LinearProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Warning,
  LocalShipping,
  Inventory,
  Assessment,
  Refresh,
} from '@mui/icons-material';
import { useDashboard } from '../hooks/useDashboard';
import { useAlerts } from '../hooks/useAlerts';
import { useWaste } from '../hooks/useWaste';
import { useDemand } from '../hooks/useDemand';
import { formatDate, formatCurrency, formatQuantity, calculatePercentage } from '../utils/format';
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
  const [selectedDateRange, setSelectedDateRange] = useState<{ start: Date; end: Date }>({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    end: new Date(),
  });
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const {
    metrics,
    isLoading: metricsLoading,
    error: metricsError,
    refetch: refetchMetrics,
  } = useDashboard();

  const {
    alerts,
    isLoading: alertsLoading,
    error: alertsError,
    refetch: refetchAlerts,
  } = useAlerts();

  const {
    wasteByProduct,
    isLoading: wasteLoading,
    error: wasteError,
    fetchWasteByProduct,
  } = useWaste();

  const {
    prediction,
    isLoading: predictionLoading,
    error: predictionError,
    fetchPrediction,
  } = useDemand();

  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    try {
      await Promise.all([
        refetchMetrics(),
        refetchAlerts(),
      ]);
      if (selectedDateRange) {
        await fetchWasteByProduct({
          startDate: selectedDateRange.start.toISOString(),
          endDate: selectedDateRange.end.toISOString(),
        });
      }
      if (selectedProductId) {
        await fetchPrediction({
          productId: selectedProductId,
          date: new Date().toISOString(),
        });
      }
    } catch (error) {
      console.error('Error refreshing dashboard data:', error);
    } finally {
      setIsRefreshing(false);
    }
  }, [refetchMetrics, refetchAlerts, fetchWasteByProduct, fetchPrediction, selectedDateRange, selectedProductId]);

  useEffect(() => {
    if (selectedDateRange) {
      fetchWasteByProduct({
        startDate: selectedDateRange.start.toISOString(),
        endDate: selectedDateRange.end.toISOString(),
      });
    }
  }, [selectedDateRange, fetchWasteByProduct]);

  useEffect(() => {
    if (selectedProductId) {
      fetchPrediction({
        productId: selectedProductId,
        date: new Date().toISOString(),
      });
    }
  }, [selectedProductId, fetchPrediction]);

  const getSeverityColor = (severity: string): 'success' | 'warning' | 'error' | 'info' => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      default:
        return 'success';
    }
  };

  const criticalAlerts = alerts?.filter((a: Alert) => a.severity === 'critical') || [];
  const warningAlerts = alerts?.filter((a: Alert) => a.severity === 'warning') || [];

  if (metricsLoading && !metrics) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          backgroundColor: '#f5f5f5',
        }}
      >
        <Box sx={{ width: '100%', maxWidth: 400, p: 3 }}>
          <LinearProgress />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2, textAlign: 'center' }}>
            Loading dashboard...
          </Typography>
        </Box>
      </Box>
    );
  }

  if (metricsError) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <MuiAlert severity="error" sx={{ mb: 2 }}>
          Error loading dashboard: {metricsError instanceof Error ? metricsError.message : 'Unknown error'}
        </MuiAlert>
      </Container>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
      <Container maxWidth="lg" sx={{ py: 3 }}>
        {/* Header */}
        <Paper
          elevation={2}
          sx={{
            p: 2,
            mb: 3,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            borderRadius: 2,
          }}
        >
          <Box>
            <Typography variant="h4" component="h1" fontWeight="bold" color="primary">
              Merma Optimization Dashboard
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Monitor waste, alerts, and recommendations for your stores
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Tooltip title="Refresh data">
              <IconButton onClick={handleRefresh} disabled={isRefreshing}>
                <Refresh className={isRefreshing ? 'rotating' : ''} />
              </IconButton>
            </Tooltip>
          </Box>
        </Paper>

        {/* Critical Alerts Banner */}
        {criticalAlerts.length > 0 && (
          <MuiAlert
            severity="error"
            sx={{ mb: 3 }}
            icon={<Warning />}
          >
            <Typography variant="subtitle2" fontWeight="bold">
              {criticalAlerts.length} Critical Alert{criticalAlerts.length > 1 ? 's' : ''} Require Immediate Attention
            </Typography>
          </MuiAlert>
        )}

        {/* Metrics Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card
              elevation={2}
              sx={{
                borderRadius: 2,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography variant="caption" sx={{ opacity: 0.8 }}>
                      Total Waste Cost
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {formatCurrency(metrics?.total_waste_cost || 0)}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                      <TrendingDown sx={{ fontSize: 16, mr: 0.5 }} />
                      <Typography variant="caption" sx={{ opacity: 0.8 }}>
                        Last 30 days
                      </Typography>
                    </Box>
                  </Box>
                  <Assessment sx={{ fontSize: 40, opacity: 0.3 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card
              elevation={2}
              sx={{
                borderRadius: 2,
                background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                color: 'white',
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography variant="caption" sx={{ opacity: 0.8 }}>
                      Total Waste Quantity
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {formatQuantity(metrics?.total_waste_quantity || 0)}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                      <TrendingDown sx={{ fontSize: 16, mr: 0.5 }} />
                      <Typography variant="caption" sx={{ opacity: 0.8 }}>
                        Units/kg
                      </Typography>
                    </Box>
                  </Box>
                  <Inventory sx={{ fontSize: 40, opacity: 0.3 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card
              elevation={2}
              sx={{
                borderRadius: 2,
                background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                color: 'white',
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography variant="caption" sx={{ opacity: 0.8 }}>
                      Active Alerts
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {alerts?.length || 0}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 1, gap: 0.5 }}>
                      <Chip
                        size="small"
                        label={`${criticalAlerts.length} critical`}
                        color="error"
                        sx={{ height: 20, fontSize: '0.7rem' }}
                      />
                      <Chip
                        size="small"
                        label={`${warningAlerts.length} warning`}
                        color="warning"
                        sx={{ height: 20, fontSize: '0.7rem' }}
                      />
                    </Box>
                  </Box>
                  <Warning sx={{ fontSize: 40, opacity: 0.3 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card
              elevation={2}
              sx={{
                borderRadius: 2,
                background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
                color: 'white',
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography variant="caption" sx={{ opacity: 0.8 }}>
                      Demand Prediction
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {metrics?.demand_prediction !== undefined
                        ? formatQuantity(metrics.demand_prediction)
                        : '--'}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                      <TrendingUp sx={{ fontSize: 16, mr: 0.5 }} />
                      <Typography variant="caption" sx={{ opacity: 0.8 }}>
                        Next 7 days
                      </Typography>
                    </Box>
                  </Box>
                  <LocalShipping sx={{ fontSize: 40, opacity: 0.3 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Main Content Grid */}
        <Grid container spacing={3}>
          {/* Waste Trend Chart */}
          <Grid item xs={12} lg={8}>
            <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Waste Trend
              </Typography>
              <Box sx={{ height: 350 }}>
                {metrics?.waste_trend && metrics.waste_trend.length > 0 ? (
                  <WasteChart data={metrics.waste_trend} />
                ) : (
                  <Box
                    sx={{
                      display: 'flex',
                      justifyContent: 'center',
                      alignItems: 'center',
                      height: '100%',
                      color: 'text.secondary',
                    }}
                  >
                    <Typography>No trend data available</Typography>
                  </Box>
                )}
              </Box>
            </Paper>
          </Grid>

          {/* Alerts List */}
          <Grid item xs={12} lg={4}>
            <Paper elevation={2} sx={{ p: 3, borderRadius: 2, height: '100%' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" fontWeight="bold">
                  Alerts
                </Typography>
                <Chip
                  label={alerts?.length || 0}
                  color={alerts && alerts.length > 0 ? 'primary' : 'default'}
                  size="small"
                />
              </Box>
              <Box sx={{ maxHeight: 300, overflowY: 'auto' }}>
                {alertsLoading ? (
                  <LinearProgress />
                ) : alertsError ? (
                  <MuiAlert severity="error">
                    Error loading alerts
                  </MuiAlert>
                ) : alerts && alerts.length > 0 ? (
                  <AlertsList alerts={alerts} maxItems={10} />
                ) : (
                  <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                    No active alerts
                  </Typography>
                )}
              </Box>
            </Paper>
          </Grid>

          {/* Waste by Product Table */}
          <Grid item xs={12} lg={8}>
            <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Waste by Product
              </Typography>
              <Box sx={{ maxHeight: 400, overflowY: 'auto' }}>
                {wasteLoading ? (
                  <LinearProgress />
                ) : wasteError ? (
                  <MuiAlert severity="error">
                    Error loading waste data
                  </MuiAlert>
                ) : wasteByProduct && wasteByProduct.length > 0 ? (
                  <WasteByProductTable data={wasteByProduct} />
                ) : (
                  <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                    No waste data available for the selected period
                  </Typography>
                )}
              </Box>
            </Paper>
          </Grid>

          {/* Demand Prediction */}
          <Grid item xs={12} lg={4}>
            <Paper elevation={2} sx={{ p: 3, borderRadius: 2, height: '100%' }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Demand Forecast
              </Typography>
              <DemandPredictionCard
                prediction={prediction}
                isLoading={predictionLoading}
                error={predictionError}
                onProductSelect={setSelectedProductId}
                selectedProductId={selectedProductId}
              />
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}
