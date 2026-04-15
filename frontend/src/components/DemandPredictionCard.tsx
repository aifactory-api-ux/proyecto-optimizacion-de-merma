import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material';
import { TrendingUp, Assessment } from '@mui/icons-material';
import type { DemandPredictionResponse } from '../types';
import { formatNumber } from '../utils/format';

interface DemandPredictionCardProps {
  prediction: DemandPredictionResponse | null;
  isLoading: boolean;
  error: Error | null;
  onProductSelect: (id: number | null) => void;
  selectedProductId: number | null;
}

export default function DemandPredictionCard({
  prediction,
  isLoading,
  error,
  onProductSelect,
  selectedProductId,
}: DemandPredictionCardProps) {
  const [inputValue, setInputValue] = useState<string>(
    selectedProductId !== null ? String(selectedProductId) : ''
  );

  const handleSearch = () => {
    const id = parseInt(inputValue, 10);
    onProductSelect(isNaN(id) || id <= 0 ? null : id);
  };

  return (
    <Card sx={{ height: '100%', minHeight: 200 }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <Assessment color="primary" />
          <Typography variant="h6" fontWeight="bold">
            Predicción de Demanda
          </Typography>
        </Box>

        {/* Product selector */}
        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
          <TextField
            label="ID de Producto"
            type="number"
            size="small"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            inputProps={{ min: 1 }}
            sx={{ flex: 1 }}
          />
          <Button
            variant="contained"
            size="small"
            onClick={handleSearch}
            disabled={isLoading || !inputValue}
          >
            Buscar
          </Button>
        </Box>

        {/* Loading */}
        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
            <CircularProgress size={32} />
          </Box>
        )}

        {/* Error */}
        {!isLoading && error && (
          <Alert severity="error" sx={{ mt: 1 }}>
            {error.message}
          </Alert>
        )}

        {/* Result */}
        {!isLoading && !error && prediction && (
          <Box sx={{ mt: 1 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Demanda prevista para los próximos 7 días
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1 }}>
              <Typography variant="h3" fontWeight="bold">
                {formatNumber(prediction.demand_prediction, 0)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                unidades
              </Typography>
            </Box>
            <Chip
              icon={<TrendingUp />}
              label={`Producto #${selectedProductId}`}
              color="primary"
              variant="outlined"
              size="small"
              sx={{ mt: 1 }}
            />
          </Box>
        )}

        {/* Empty state */}
        {!isLoading && !error && !prediction && (
          <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
            Ingrese un ID de producto para ver la predicción.
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}
