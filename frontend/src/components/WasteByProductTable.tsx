import React, { useState, useMemo } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TextField,
  Box,
  Typography,
  CircularProgress,
  Alert,
  TableSortLabel,
} from '@mui/material';
import { getWasteByProduct } from '../api/waste';
import { WasteMetric } from '../types';
import { formatCurrency, formatDate } from '../utils/format';

type SortField = 'product_name' | 'waste_quantity' | 'waste_cost' | 'date';
type SortOrder = 'asc' | 'desc';

interface WasteByProductTableProps {
  token: string;
  initialStartDate?: string;
  initialEndDate?: string;
}

export default function WasteByProductTable({
  token,
  initialStartDate,
  initialEndDate,
}: WasteByProductTableProps) {
  const [startDate, setStartDate] = useState<string>(
    initialStartDate || new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  );
  const [endDate, setEndDate] = useState<string>(
    initialEndDate || new Date().toISOString().split('T')[0]
  );
  const [data, setData] = useState<WasteMetric[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [sortField, setSortField] = useState<SortField>('waste_cost');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');

  const fetchData = React.useCallback(async () => {
    if (!startDate || !endDate) {
      setError('Please provide both start and end dates');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await getWasteByProduct(token, startDate, endDate);
      setData(result);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch waste data';
      setError(errorMessage);
      console.error('Error fetching waste by product:', err);
    } finally {
      setLoading(false);
    }
  }, [token, startDate, endDate]);

  React.useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  const sortedData = useMemo(() => {
    if (!data || data.length === 0) return [];

    return [...data].sort((a, b) => {
      let aVal: string | number = 0;
      let bVal: string | number = 0;

      switch (sortField) {
        case 'product_name':
          aVal = a.product_name || '';
          bVal = b.product_name || '';
          break;
        case 'waste_quantity':
          aVal = a.waste_quantity || 0;
          bVal = b.waste_quantity || 0;
          break;
        case 'waste_cost':
          aVal = a.waste_cost || 0;
          bVal = b.waste_cost || 0;
          break;
        case 'date':
          aVal = a.date || '';
          bVal = b.date || '';
          break;
      }

      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return sortOrder === 'asc'
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      }

      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
      }

      return 0;
    });
  }, [data, sortField, sortOrder]);

  const totalQuantity = useMemo(() => {
    return sortedData.reduce((sum, item) => sum + (item.waste_quantity || 0), 0);
  }, [sortedData]);

  const totalCost = useMemo(() => {
    return sortedData.reduce((sum, item) => sum + (item.waste_cost || 0), 0);
  }, [sortedData]);

  return (
    <Box sx={{ width: '100%' }}>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box
          sx={{
            display: 'flex',
            gap: 2,
            flexWrap: 'wrap',
            alignItems: 'center',
            mb: 2,
          }}
        >
          <TextField
            label="Start Date"
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            InputLabelProps={{ shrink: true }}
            size="small"
            data-testid="start-date-input"
          />
          <TextField
            label="End Date"
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            InputLabelProps={{ shrink: true }}
            size="small"
            data-testid="end-date-input"
          />
          <button
            onClick={fetchData}
            disabled={loading}
            style={{
              padding: '8px 16px',
              backgroundColor: '#1976d2',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1,
            }}
          >
            {loading ? 'Loading...' : 'Filter'}
          </button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ display: 'flex', gap: 3, mb: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Total Quantity Wasted: <strong>{totalQuantity.toFixed(2)}</strong>
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Total Cost: <strong>{formatCurrency(totalCost)}</strong>
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Products: <strong>{sortedData.length}</strong>
          </Typography>
        </Box>
      </Paper>

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {!loading && sortedData.length === 0 && !error && (
        <Alert severity="info">
          No waste data available for the selected date range.
        </Alert>
      )}

      {!loading && sortedData.length > 0 && (
        <TableContainer component={Paper}>
          <Table sx={{ minWidth: 650 }} aria-label="waste by product table">
            <TableHead>
              <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                <TableCell>
                  <TableSortLabel
                    active={sortField === 'date'}
                    direction={sortField === 'date' ? sortOrder : 'asc'}
                    onClick={() => handleSort('date')}
                  >
                    Date
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortField === 'product_name'}
                    direction={sortField === 'product_name' ? sortOrder : 'asc'}
                    onClick={() => handleSort('product_name')}
                  >
                    Product
                  </TableSortLabel>
                </TableCell>
                <TableCell align="right">
                  <TableSortLabel
                    active={sortField === 'waste_quantity'}
                    direction={sortField === 'waste_quantity' ? sortOrder : 'asc'}
                    onClick={() => handleSort('waste_quantity')}
                  >
                    Quantity Wasted
                  </TableSortLabel>
                </TableCell>
                <TableCell align="right">
                  <TableSortLabel
                    active={sortField === 'waste_cost'}
                    direction={sortField === 'waste_cost' ? sortOrder : 'asc'}
                    onClick={() => handleSort('waste_cost')}
                  >
                    Cost
                  </TableSortLabel>
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sortedData.map((row, index) => (
                <TableRow
                  key={`${row.product_id}-${row.date}-${index}`}
                  sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                >
                  <TableCell component="th" scope="row">
                    {row.date ? formatDate(row.date) : '-'}
                  </TableCell>
                  <TableCell>{row.product_name || `Product #${row.product_id}`}</TableCell>
                  <TableCell align="right">
                    {(row.waste_quantity || 0).toFixed(2)}
                  </TableCell>
                  <TableCell align="right">
                    {formatCurrency(row.waste_cost || 0)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}
