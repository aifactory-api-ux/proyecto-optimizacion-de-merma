import React, { useState, useMemo } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Box,
  Typography,
  TableSortLabel,
} from '@mui/material';
import type { WasteByProductResponse } from '../types';
import { formatCurrency, formatDate } from '../utils/format';

type SortField = 'product_name' | 'waste_quantity' | 'waste_cost' | 'date';
type SortOrder = 'asc' | 'desc';

interface WasteByProductTableProps {
  data: WasteByProductResponse[];
}

export default function WasteByProductTable({ data }: WasteByProductTableProps) {
  const [sortField, setSortField] = useState<SortField>('waste_cost');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');

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
        return sortOrder === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      }
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
      }
      return 0;
    });
  }, [data, sortField, sortOrder]);

  const totalQuantity = useMemo(() =>
    sortedData.reduce((sum, item) => sum + (item.waste_quantity || 0), 0),
    [sortedData]
  );

  const totalCost = useMemo(() =>
    sortedData.reduce((sum, item) => sum + (item.waste_cost || 0), 0),
    [sortedData]
  );

  if (sortedData.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
        No hay datos de merma disponibles para el período seleccionado.
      </Typography>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ display: 'flex', gap: 3, mb: 2 }}>
        <Typography variant="body2" color="text.secondary">
          Cantidad total: <strong>{totalQuantity.toFixed(2)}</strong>
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Costo total: <strong>{formatCurrency(totalCost)}</strong>
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Productos: <strong>{sortedData.length}</strong>
        </Typography>
      </Box>

      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 500 }} aria-label="waste by product table">
          <TableHead>
            <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
              <TableCell>
                <TableSortLabel
                  active={sortField === 'date'}
                  direction={sortField === 'date' ? sortOrder : 'asc'}
                  onClick={() => handleSort('date')}
                >
                  Fecha
                </TableSortLabel>
              </TableCell>
              <TableCell>
                <TableSortLabel
                  active={sortField === 'product_name'}
                  direction={sortField === 'product_name' ? sortOrder : 'asc'}
                  onClick={() => handleSort('product_name')}
                >
                  Producto
                </TableSortLabel>
              </TableCell>
              <TableCell align="right">
                <TableSortLabel
                  active={sortField === 'waste_quantity'}
                  direction={sortField === 'waste_quantity' ? sortOrder : 'asc'}
                  onClick={() => handleSort('waste_quantity')}
                >
                  Cantidad
                </TableSortLabel>
              </TableCell>
              <TableCell align="right">
                <TableSortLabel
                  active={sortField === 'waste_cost'}
                  direction={sortField === 'waste_cost' ? sortOrder : 'asc'}
                  onClick={() => handleSort('waste_cost')}
                >
                  Costo
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
                <TableCell>{row.date ? formatDate(row.date) : '-'}</TableCell>
                <TableCell>{row.product_name || `Producto #${row.product_id}`}</TableCell>
                <TableCell align="right">{(row.waste_quantity || 0).toFixed(2)}</TableCell>
                <TableCell align="right">{formatCurrency(row.waste_cost || 0)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}
