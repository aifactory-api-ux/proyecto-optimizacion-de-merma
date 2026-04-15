import React from 'react';
import { Card, CardContent, CardHeader, Typography, Box, Chip, Alert, AlertTitle } from '@mui/material';
import { TrendingUp, TrendingDown, TrendingFlat, Inventory, Assessment } from '@mui/icons-material';
import { formatNumber, formatCurrency, formatDate } from '../utils/format';

/**
 * DemandPredictionCard Component
 * 
 * Displays demand prediction for a product on a given date.
 * Shows the predicted demand quantity, confidence level,
 * and visual indicators for the prediction trend.
 * 
 * Props:
 * - prediction: The predicted demand value
 * - confidence: Confidence level (0-1)
 * - productName: Name of the product
 * - date: Date for which prediction is made
 * - previousPrediction: Optional previous prediction for trend comparison
 * - onRefresh: Optional callback to refresh prediction
 */

interface DemandPredictionCardProps {
  prediction: number;
  confidence: number;
  productName: string;
  date: string;
  previousPrediction?: number;
  onRefresh?: () => void;
  loading?: boolean;
  error?: string;
}

export function DemandPredictionCard({
  prediction,
  confidence,
  productName,
  date,
  previousPrediction,
  onRefresh,
  loading = false,
  error
}: DemandPredictionCardProps) {
  // Determine trend direction
  const getTrendDirection = (): 'up' | 'down' | 'flat' => {
    if (!previousPrediction) return 'flat';
    const diff = prediction - previousPrediction;
    if (diff > 0.05 * previousPrediction) return 'up';
    if (diff < -0.05 * previousPrediction) return 'down';
    return 'flat';
  };

  const trend = getTrendDirection();

  // Get confidence level label
  const getConfidenceLabel = (conf: number): { label: string; color: 'success' | 'warning' | 'error' } => {
    if (conf >= 0.8) return { label: 'Alta', color: 'success' };
    if (conf >= 0.6) return { label: 'Media', color: 'warning' };
    return { label: 'Baja', color: 'error' };
  };

  const confidenceInfo = getConfidenceLabel(confidence);

  // Get trend icon and color
  const getTrendInfo = () => {
    switch (trend) {
      case 'up':
        return { icon: <TrendingUp />, color: 'success', label: 'Aumento' };
      case 'down':
        return { icon: <TrendingDown />, color: 'error', label: 'Disminución' };
      default:
        return { icon: <TrendingFlat />, color: 'info', label: 'Estable' };
    }
  };

  const trendInfo = getTrendInfo();

  // Handle loading state
  if (loading) {
    return (
      <Card sx={{ height: '100%', minHeight: 200 }}>
        <CardHeader
          title="Predicción de Demanda"
          subheader={productName}
          avatar={<Assessment color="primary" />}
        />
        <CardContent>
          <Box
            display="flex"
            justifyContent="center"
            alignItems="center"
            minHeight: 100
          >
            <Typography variant="body2" color="text.secondary">
              Cargando predicción...
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  // Handle error state
  if (error) {
    return (
      <Card sx={{ height: '100%', minHeight: 200 }}>
        <CardHeader
          title="Predicción de Demanda"
          subheader={productName}
          avatar={<Assessment color="primary" />}
        />
        <CardContent>
          <Alert severity="error">
            <AlertTitle>Error</AlertTitle>
            {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  // Main content
  return (
    <Card sx={{ height: '100%', minHeight: 200 }}>
      <CardHeader
        title="Predicción de Demanda"
        subheader={`${productName} - ${formatDate(date)}`}
        avatar={<Assessment color="primary" />}
        action={
          onRefresh && (
            <Box
              component="button"
              onClick={onRefresh}
              sx={{
                border: 'none',
                background: 'transparent',
                cursor: 'pointer',
                p: 1,
                borderRadius: 1,
                '&:hover': { backgroundColor: 'action.hover' }
              }}
              aria-label="Actualizar predicción"
            >
              <Inventory color="action" />
            </Box>
          )
        }
      />
      <CardContent>
        <Box display="flex" flexDirection="column" gap={2}>
          {/* Main prediction value */}
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Demanda Prevista
            </Typography>
            <Typography variant="h3" component="div" fontWeight="bold">
              {formatNumber(prediction)}
              <Typography
                component="span"
                variant="body2"
                color="text.secondary"
                sx={{ ml: 1 }}
              >
                unidades
              </Typography>
            </Typography>
          </Box>

          {/* Confidence and trend indicators */}
          <Box display="flex" gap={1} flexWrap="wrap">
            <Chip
              icon={<Inventory />}
              label={`Confianza: ${(confidence * 100).toFixed(0)}%`}
              color={confidenceInfo.color}
              variant="outlined"
              size="small"
            />
            {previousPrediction !== undefined && (
              <Chip
                icon={trendInfo.icon}
                label={`vs anterior: ${trendInfo.label}`}
                color={trendInfo.color}
                variant="outlined"
                size="small"
              />
            )}
          </Box>

          {/* Metadata */}
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            sx={{ mt: 1, pt: 1, borderTop: 1, borderColor: 'divider' }}
          >
            <Typography variant="caption" color="text.secondary">
              Fecha: {formatDate(date)}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Actualizado: {formatDate(new Date().toISOString())}
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}

/**
 * DemandPredictionCardSkeleton Component
 * 
 * Loading skeleton for DemandPredictionCard.
 */
export function DemandPredictionCardSkeleton() {
  return (
    <Card sx={{ height: '100%', minHeight: 200 }}>
      <CardHeader
        title="Cargando..."
        subheader="Esperando datos"
        avatar={<Assessment />}
      />
      <CardContent>
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          minHeight: 100
        >
          <Typography variant="body2" color="text.secondary">
            Cargando predicción de demanda...
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}

export default DemandPredictionCard;
