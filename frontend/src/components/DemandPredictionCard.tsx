import React, { useState } from 'react';
import { CircularProgress } from '@mui/material';
import { TrendingUp } from '@mui/icons-material';
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

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSearch();
  };

  return (
    <div>
      {/* Product selector */}
      <div style={{ display: 'flex', gap: 'var(--sp-2)', marginBottom: 'var(--sp-4)' }}>
        <input
          className="field-input"
          type="number"
          min={1}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="ID de producto…"
          style={{ flex: 1 }}
        />
        <button
          className="btn btn--primary"
          onClick={handleSearch}
          disabled={isLoading || !inputValue}
          style={{ flexShrink: 0 }}
        >
          Buscar
        </button>
      </div>

      {/* Loading */}
      {isLoading && (
        <div style={{ display: 'flex', justifyContent: 'center', padding: 'var(--sp-6)' }}>
          <CircularProgress size={32} />
        </div>
      )}

      {/* Error */}
      {!isLoading && error && (
        <div className="alert-strip alert-strip--error">
          <span>⚠</span> {error.message}
        </div>
      )}

      {/* Result */}
      {!isLoading && !error && prediction && (
        <div className="demand-result">
          <div style={{
            fontSize: 'var(--text-xs)',
            fontWeight: 600,
            color: 'var(--clr-text-2)',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            marginBottom: 'var(--sp-2)',
          }}>
            Demanda prevista — próximos 7 días
          </div>
          <div className="demand-result-value">
            {formatNumber(prediction.demand_prediction, 0)}
          </div>
          <div className="demand-result-unit">unidades</div>
          <div style={{ marginTop: 'var(--sp-3)' }}>
            <span className="chip chip--primary">
              <TrendingUp style={{ fontSize: 12 }} />
              Producto #{selectedProductId}
            </span>
          </div>
        </div>
      )}

      {/* Empty state */}
      {!isLoading && !error && !prediction && (
        <div className="empty-state">
          <span className="empty-state-icon">🔍</span>
          <span className="empty-state-text">
            Ingrese un ID de producto y presione Buscar para ver la predicción.
          </span>
        </div>
      )}
    </div>
  );
}
