import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts';
import { Card, CardContent, CardHeader, Typography, Box, CircularProgress, Alert, useTheme } from '@mui/material';
import { WasteMetric } from '../types';

interface WasteChartProps {
  data: WasteMetric[];
  isLoading?: boolean;
  error?: string | null;
  variant?: 'line' | 'area';
  showQuantity?: boolean;
  showCost?: boolean;
  title?: string;
  height?: number;
  colorBase?: string;
}

const WasteChart: React.FC<WasteChartProps> = ({
  data,
  isLoading = false,
  error = null,
  variant = 'line',
  showQuantity = true,
  showCost = true,
  title = 'Waste Trend',
  height = 300,
  colorBase = '#1976d2',
}) => {
  const theme = useTheme();

  const formattedData = useMemo(() => {
    if (!data || !Array.isArray(data)) {
      return [];
    }
    
    return data.map((item: WasteMetric) => ({
      ...item,
      dateFormatted: new Date(item.date).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      }),
      dateFull: new Date(item.date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      }),
    }));
  }, [data]);


  const formatYAxis = (value: number): string => {
    if (value >= 1000) {
      return `${(value / 1000).toFixed(1)}k`;
    }
    return value.toFixed(0);
  };

  const formatTooltipValue = (value: number, name: string): string => {
    if (name === 'waste_cost') {
      return `$${value.toFixed(2)}`;
    }
    return value.toFixed(2);
  };

  const customizeTooltip = ({ active, payload, label }: { active?: boolean; payload?: Array<{ value: number; name: string; color: string }>; label?: string }) => {
    if (!active || !payload || payload.length === 0) {
      return null;
    }

    return (
      <Box
        sx={{
          bgcolor: 'background.paper',
          p: 1.5,
          border: '1px solid',
          borderColor: 'divider',
          borderRadius: 1,
          boxShadow: 2,
        }}
      >
        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 0.5 }}>
          {label}
        </Typography>
        {payload.map((entry, index) => (
          <Typography
            key={index}
            variant="body2"
            sx={{ color: entry.color, display: 'block' }}
          >
            {entry.name === 'waste_quantity' ? 'Quantity: ' : 'Cost: '}
            {formatTooltipValue(entry.value, entry.name)}
          </Typography>
        ))}
      </Box>
    );
  };

  const renderChart = () => {
    const chartProps = {
      data: formattedData,
      margin: {
        top: 10,
        right: 30,
        left: 0,
        bottom: 0,
      },
    };

    if (variant === 'area') {
      return (
        <AreaChart {...chartProps}>
          <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
          <XAxis
            dataKey="dateFormatted"
            tick={{ fontSize: 12 }}
            stroke={theme.palette.text.secondary}
          />
          <YAxis
            tickFormatter={formatYAxis}
            tick={{ fontSize: 12 }}
            stroke={theme.palette.text.secondary}
          />
          <Tooltip content={customizeTooltip} />
          <Legend />
          {showQuantity && (
            <Area
              type="monotone"
              dataKey="waste_quantity"
              name="Waste Quantity"
              stroke={colorBase}
              fill={colorBase}
              fillOpacity={0.3}
              strokeWidth={2}
              animationDuration={500}
            />
          )}
          {showCost && (
            <Area
              type="monotone"
              dataKey="waste_cost"
              name="Waste Cost"
              stroke="#f50057"
              fill="#f50057"
              fillOpacity={0.2}
              strokeWidth={2}
              animationDuration={500}
            />
          )}
        </AreaChart>
      );
    }

    return (
      <LineChart {...chartProps}>
        <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
        <XAxis
          dataKey="dateFormatted"
          tick={{ fontSize: 12 }}
          stroke={theme.palette.text.secondary}
        />
        <YAxis
          tickFormatter={formatYAxis}
          tick={{ fontSize: 12 }}
          stroke={theme.palette.text.secondary}
        />
        <Tooltip content={customizeTooltip} />
        <Legend />
        {showQuantity && (
          <Line
            type="monotone"
            dataKey="waste_quantity"
            name="Waste Quantity"
            stroke={colorBase}
            strokeWidth={2}
            dot={{ r: 4, strokeWidth: 2 }}
            activeDot={{ r: 6 }}
            animationDuration={500}
          />
        )}
        {showCost && (
          <Line
            type="monotone"
            dataKey="waste_cost"
            name="Waste Cost"
            stroke="#f50057"
            strokeWidth={2}
            dot={{ r: 4, strokeWidth: 2 }}
            activeDot={{ r: 6 }}
            animationDuration={500}
          />
        )}
      </LineChart>
    );
  };

  if (isLoading) {
    return (
      <Card sx={{ height: '100%', minHeight: height }}>
        <CardHeader
          title={title}
          titleTypographyProps={{ variant: 'h6' }}
          sx={{ pb: 0 }}
        />
        <CardContent
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            height: height,
          }}
        >
          <CircularProgress />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card sx={{ height: '100%', minHeight: height }}>
        <CardHeader
          title={title}
          titleTypographyProps={{ variant: 'h6' }}
          sx={{ pb: 0 }}
        />
        <CardContent>
          <Alert severity="error" sx={{ width: '100%' }}>
            {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!formattedData || formattedData.length === 0) {
    return (
      <Card sx={{ height: '100%', minHeight: height }}>
        <CardHeader
          title={title}
          titleTypographyProps={{ variant: 'h6' }}
          sx={{ pb: 0 }}
        />
        <CardContent
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            height: height,
          }}
        >
          <Typography variant="body2" color="text.secondary">
            No data available
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ height: '100%', minHeight: height }}>
      <CardHeader
        title={title}
        titleTypographyProps={{ variant: 'h6' }}
        sx={{ pb: 0 }}
      />
      <CardContent>
        <Box sx={{ width: '100%', height }}>
          <ResponsiveContainer width="100%" height="100%">
            {renderChart()}
          </ResponsiveContainer>
        </Box>
      </CardContent>
    </Card>
  );
};

export default WasteChart;
